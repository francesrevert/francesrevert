---
name: registrar-finanzas
description: Registra de forma cifrada ingresos, gastos únicos, gastos mensuales, suscripciones anuales y compras a plazos en Finanzas · Manolo y María. Usar cuando Manolo o María pidan en ChatGPT añadir, apuntar, registrar o guardar un movimiento financiero en su aplicación.
---

# Registrar Finanzas

Crear una orden cifrada sin solicitar ni recibir la contraseña de la aplicación.

## Flujo obligatorio

1. Interpretar el movimiento. Preguntar solo si falta un dato imprescindible que no pueda inferirse con seguridad.
2. Usar la fecha actual en la zona horaria del usuario cuando diga «hoy». Mantener importes como números positivos; el tipo indica si es ingreso o gasto.
3. Usar la acción `fetch_file` del complemento GitHub para obtener `chat-public-key.json` de la rama `data` del repositorio `francesrevert/francesrevert.github.io`.
4. Si no existe, indicar únicamente: «Abre Finanzas una vez con tu contraseña y vuelve a intentarlo».
5. Preparar un JSON con `kind`, `name`, `amount`, `date`, `recurrence`, `status`, `notes` y los campos opcionales aplicables.
6. Ejecutar `scripts/encrypt_entry.py` con el JSON del movimiento y la clave pública. No reproducir la contraseña, el token ni datos anteriores.
7. Leer solamente el archivo cifrado resultante.
8. Usar la acción `create_file` del complemento GitHub para crear un archivo nuevo en la rama `data`, con ruta `chat-inbox/<id>.json`, contenido idéntico al cifrado y mensaje `finanzas: añadir movimiento cifrado`.
9. Confirmar de forma breve: «Movimiento preparado. Se incorporará al abrir Finanzas».

## Clasificación

- Ingreso puntual: `kind=income`, `recurrence=once`.
- Ingreso mensual: `kind=income`, `recurrence=monthly`.
- Gasto puntual: `kind=expense`, `recurrence=once`.
- Gasto mensual recurrente: `kind=expense`, `recurrence=monthly`.
- Suscripción o gasto anual: `kind=expense`, `recurrence=annual`.
- Compra a plazos: `kind=expense`, `recurrence=installments`, incluyendo `installments` y, solo si procede, `finalAmount`.

Usar `status=paid` cuando el usuario diga que ya se ha cobrado o pagado. En los demás casos usar `status=planned`.

## Límites de seguridad

- No pedir nunca la contraseña de Finanzas ni un token de GitHub.
- No escribir movimientos sin cifrar en GitHub, comentarios, PR, mensajes de commit o respuestas.
- No modificar `vault.json`, `chat-public-key.json` ni archivos ya existentes de `chat-inbox`.
- No inventar importe, concepto, recurrencia o número de cuotas.
- Crear un archivo por movimiento; para varios movimientos, cifrar y crear cada uno por separado.
