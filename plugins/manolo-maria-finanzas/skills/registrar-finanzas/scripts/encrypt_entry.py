#!/usr/bin/env python3
"""Encrypt one finance movement for the GitHub-backed chat inbox."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


ALGORITHM = "RSA-OAEP-256+A256GCM"
ALLOWED_KINDS = {"income", "expense"}
ALLOWED_RECURRENCES = {"once", "monthly", "annual", "installments"}
ALLOWED_STATUSES = {"planned", "paid"}


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} debe contener un objeto JSON")
    return value


def required_text(value: object, field: str, maximum: int) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum:
        raise ValueError(f"{field} no es válido")
    return text


def optional_text(value: object, field: str, maximum: int) -> str:
    text = str(value or "").strip()
    if len(text) > maximum:
        raise ValueError(f"{field} es demasiado largo")
    return text


def validate_date(value: object) -> str:
    text = required_text(value, "date", 10)
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("date debe usar YYYY-MM-DD") from exc
    return text


def normalize_movement(source: dict) -> dict:
    kind = str(source.get("kind", "")).strip().lower()
    recurrence = str(source.get("recurrence", "")).strip().lower()
    status = str(source.get("status", "planned")).strip().lower()
    if kind not in ALLOWED_KINDS:
        raise ValueError("kind debe ser income o expense")
    if recurrence not in ALLOWED_RECURRENCES:
        raise ValueError("recurrence no es compatible")
    if status not in ALLOWED_STATUSES:
        raise ValueError("status debe ser planned o paid")
    if kind == "income" and recurrence in {"annual", "installments"}:
        raise ValueError("esa recurrencia no está disponible para ingresos")

    try:
        amount = round(float(source.get("amount")), 2)
    except (TypeError, ValueError) as exc:
        raise ValueError("amount debe ser un número") from exc
    if not 0 < amount <= 100_000_000:
        raise ValueError("amount está fuera de rango")

    movement = {
        "kind": kind,
        "name": required_text(source.get("name"), "name", 160),
        "amount": amount,
        "date": validate_date(source.get("date")),
        "recurrence": recurrence,
        "status": status,
        "notes": optional_text(source.get("notes"), "notes", 2000),
    }
    category = optional_text(source.get("category"), "category", 120)
    if category:
        movement["category"] = category

    if recurrence == "installments":
        try:
            installments = int(source.get("installments"))
        except (TypeError, ValueError) as exc:
            raise ValueError("installments debe ser un entero") from exc
        if not 2 <= installments <= 36:
            raise ValueError("installments debe estar entre 2 y 36")
        movement["installments"] = installments
        if source.get("finalAmount") not in (None, ""):
            final_amount = round(float(source["finalAmount"]), 2)
            if not 0 < final_amount <= 100_000_000:
                raise ValueError("finalAmount está fuera de rango")
            movement["finalAmount"] = final_amount
    return movement


def cryptography_encrypt(public_jwk: dict, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes, bytes]:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    public_key = rsa.RSAPublicNumbers(
        int.from_bytes(b64url_decode(public_jwk["e"]), "big"),
        int.from_bytes(b64url_decode(public_jwk["n"]), "big"),
    ).public_key()
    aes_key = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(iv, plaintext, aad)
    wrapped_key = public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return wrapped_key, iv, ciphertext


def pycryptodome_encrypt(public_jwk: dict, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes, bytes]:
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA

    public_key = RSA.construct((
        int.from_bytes(b64url_decode(public_jwk["n"]), "big"),
        int.from_bytes(b64url_decode(public_jwk["e"]), "big"),
    ))
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv, mac_len=16)
    cipher.update(aad)
    encrypted, tag = cipher.encrypt_and_digest(plaintext)
    wrapped_key = PKCS1_OAEP.new(public_key, hashAlgo=SHA256).encrypt(aes_key)
    return wrapped_key, iv, encrypted + tag


def encrypt(public_jwk: dict, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes, bytes]:
    try:
        return cryptography_encrypt(public_jwk, plaintext, aad)
    except ImportError:
        try:
            return pycryptodome_encrypt(public_jwk, plaintext, aad)
        except ImportError as exc:
            raise RuntimeError("El entorno de cálculo no dispone de cifrado RSA/AES") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-key", required=True, type=Path)
    parser.add_argument("--movement", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    public_key_file = load_json(args.public_key)
    if public_key_file.get("version") != 1 or public_key_file.get("algorithm") != ALGORITHM:
        raise ValueError("La clave pública no es compatible")
    key_id = required_text(public_key_file.get("keyId"), "keyId", 128)
    public_jwk = public_key_file.get("publicKey")
    if not isinstance(public_jwk, dict) or public_jwk.get("kty") != "RSA" or not public_jwk.get("n") or not public_jwk.get("e"):
        raise ValueError("La clave pública está incompleta")

    movement = normalize_movement(load_json(args.movement))
    entry_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = {
        "version": 1,
        "operation": "add_movement",
        "id": entry_id,
        "createdAt": created_at,
        "movement": movement,
    }
    plaintext = json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    aad_text = f"manolo-maria-finanzas:{entry_id}:{key_id}"
    wrapped_key, iv, ciphertext = encrypt(public_jwk, plaintext, aad_text.encode("utf-8"))
    envelope = {
        "version": 1,
        "algorithm": ALGORITHM,
        "id": entry_id,
        "keyId": key_id,
        "createdAt": created_at,
        "wrappedKey": b64url_encode(wrapped_key),
        "iv": b64url_encode(iv),
        "ciphertext": b64url_encode(ciphertext),
    }
    args.output.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"chat-inbox/{entry_id}.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"No se ha podido cifrar el movimiento: {error}", file=sys.stderr)
        raise SystemExit(1)
