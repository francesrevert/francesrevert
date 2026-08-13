# Finanzas · Manolo y María

Tabla de pagos multidispositivo publicada con GitHub Pages. Conserva la estructura de
ingresos, gastos mensuales, gastos no mensuales, suscripciones anuales, planificación por
mes, saldos, estados, fechas, notas, colores y totales.

## Modelo de seguridad

- Los datos se cifran en cada navegador con AES-256-GCM.
- La clave se deriva de la contraseña con PBKDF2-SHA256 y 600.000 iteraciones.
- GitHub solo recibe `vault.json`, cuyo contenido financiero es ilegible sin la contraseña.
- La contraseña nunca se envía a GitHub.
- El token de GitHub se conserva únicamente en memoria mientras la pestaña está abierta.
- La sesión se bloquea tras 15 minutos sin actividad.
- Cada guardado incluye el SHA leído al abrir la aplicación. Si otra persona ha guardado
  antes, GitHub devuelve un conflicto y se evita sobrescribir sus cambios.
- La clave temporal obliga a establecer una contraseña nueva en el primer acceso. La nueva
  copia cifrada se guarda en GitHub y la clave temporal deja de descifrarla en todos los
  dispositivos.

La aplicación y el repositorio son públicos. Cualquiera puede descargar el archivo cifrado,
pero no leer su contenido sin la contraseña. La confidencialidad depende del cifrado, de una
contraseña larga y exclusiva y de la seguridad de la cuenta de GitHub.

## Token de acceso por persona

La persona que gestiona el repositorio debe crear desde la cuenta `francesrevert` un token
personal de granularidad fina:

1. Abrir `https://github.com/settings/personal-access-tokens/new`.
2. Elegir como propietario del recurso `francesrevert`.
3. Limitar el token exclusivamente al repositorio `francesrevert`.
4. Conceder `Repository permissions → Contents → Read and write`.
5. Definir una fecha de caducidad corta y renovarlo cuando corresponda.

El token se introduce al abrir la web. No debe guardarse en notas, commits ni conversaciones.

## Publicación

El workflow de GitHub Actions publica solo la carpeta `docs/`. El archivo cifrado `vault.json`
permanece fuera del artefacto de Pages; la aplicación exige autenticación para leerlo y
actualizarlo mediante la API de GitHub.

La fuente de publicación de `Settings → Pages` está configurada como **GitHub Actions**. La
dirección prevista es `https://francesrevert.github.io/francesrevert/`.

## Cambios mediante ChatGPT + GitHub

La app de GitHub usada por ChatGPT debe tener acceso al repositorio. Con ese permiso se
pueden solicitar por chat cambios de diseño, comportamiento o estructura. `AGENTS.md` ordena
mantener los datos cifrados fuera del alcance del chat.

## Copias de seguridad

El botón **Backup** descarga una copia cifrada. **Restaurar** vuelve a guardar esa copia en
GitHub y bloquea la sesión para solicitar su contraseña.
