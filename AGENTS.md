# Reglas del repositorio

## Alcance

Aplicación de finanzas de Manolo y María, publicada con GitHub Pages desde `docs/`.
No usa Cloudflare ni ningún backend externo. El archivo `vault.json` de la rama `data` es el
almacén compartido y solo puede contener datos y credenciales cifrados.

## Seguridad obligatoria

- No incluir datos financieros, contraseñas, tokens ni ejemplos reales en texto claro. La
  credencial de guardado solo puede existir dentro del contenido cifrado del vault.
- No registrar ni mostrar tokens de GitHub en consola, errores o archivos.
- No debilitar AES-256-GCM, PBKDF2-SHA256, el número de iteraciones ni la CSP sin una
  justificación explícita y una revisión de seguridad.
- No mover `vault.json` a `main` ni a `docs/`: la web pública debe contener solo la aplicación.
- Conservar el control de concurrencia mediante el SHA de GitHub al actualizar el vault.
- No añadir analítica, fuentes remotas, CDN, telemetría ni solicitudes de red distintas
  de `https://api.github.com`.
- Los cambios solicitados desde ChatGPT afectan al código y a la estructura. El contenido
  financiero cifrado no debe descifrarse ni editarse desde el chat.

## Publicación

El workflow `.github/workflows/pages.yml` solo se ejecuta en `main` cuando cambia `docs/` o
el propio workflow. Las actualizaciones de `vault.json` en `data` no deben desplegar nada.

## Validación mínima

Antes de publicar:

1. Comprobar que el JavaScript incrustado pasa `node --check`.
2. Buscar referencias a datos personales, Cloudflare y rutas `/private/`.
3. Confirmar que `vault.json` tiene `forcePasswordChange` y solo metadatos cifrados.
4. Probar el diseño a anchuras de móvil y escritorio.
