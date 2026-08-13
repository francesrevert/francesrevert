# Finanzas · Manolo y María

Tabla de pagos multidispositivo publicada con GitHub Pages. Conserva la estructura de
ingresos, gastos mensuales, gastos no mensuales, suscripciones anuales, planificación por
mes, saldos, estados, fechas, notas, colores y totales.

## Modelo de seguridad

- Los datos se cifran en cada navegador con AES-256-GCM.
- La clave se deriva de la contraseña con PBKDF2-SHA256 y 600.000 iteraciones.
- GitHub solo recibe `vault.json`, cuyo contenido financiero y credencial de guardado son
  ilegibles sin la contraseña.
- La contraseña nunca se envía a GitHub.
- La credencial de GitHub permanece cifrada dentro del vault y solo existe en memoria
  mientras la sesión está abierta.
- La sesión se bloquea tras 15 minutos sin actividad.
- Cada guardado incluye el SHA leído al abrir la aplicación. Si otra persona ha guardado
  antes, GitHub devuelve un conflicto y se evita sobrescribir sus cambios.
- La clave temporal obliga a establecer una contraseña nueva en el primer acceso. La nueva
  copia cifrada se guarda en GitHub y la clave temporal deja de descifrarla en todos los
  dispositivos.

La aplicación y el repositorio son públicos. Cualquiera puede descargar el archivo cifrado,
pero no leer su contenido sin la contraseña. La confidencialidad depende del cifrado, de una
contraseña larga y exclusiva y de la seguridad de la cuenta de GitHub.

## Acceso cotidiano

Manolo y María solo tienen que introducir la contraseña. La aplicación descarga la copia
cifrada públicamente, la descifra en el navegador y utiliza internamente la credencial
incluida para guardar. La primera contraseña es temporal y obliga a crear una frase nueva de
al menos 16 caracteres.

La credencial está limitada a este repositorio, solo concede `Contents: read and write` y
caduca el 13 de agosto de 2027. Su renovación es una tarea de mantenimiento; nunca debe
facilitarse al usuario final ni guardarse en texto claro.

## Publicación

El workflow de GitHub Actions publica solo la carpeta `docs/` de `main`. El archivo cifrado
`vault.json` vive en la rama `data`, fuera del artefacto de Pages. Se lee sin autenticación y
solo puede actualizarse después de descifrar la credencial incluida.

La fuente de publicación de `Settings → Pages` está configurada como **GitHub Actions**. La
dirección prevista es `https://francesrevert.github.io/francesrevert/`.

## Cambios mediante ChatGPT + GitHub

La app de GitHub usada por ChatGPT debe tener acceso al repositorio. Con ese permiso se
pueden solicitar por chat cambios de diseño, comportamiento o estructura. `AGENTS.md` ordena
mantener los datos cifrados fuera del alcance del chat.

## Copias de seguridad

El botón **Backup** descarga una copia cifrada. **Restaurar** vuelve a guardar esa copia en
GitHub y bloquea la sesión para solicitar su contraseña.
