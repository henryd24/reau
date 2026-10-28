# Probar REau sin la moto: el tablero falso

English: [FAKE_DASH.md](FAKE_DASH.md) (es la versión de referencia; esta es su traducción).

El tablero Tripper está en la moto, y REau solo habla con él por el Wi-Fi del propio tablero. `fake_dash.py` hace de tablero en tu
computador, y un **build de debug** de REau puede apuntar a él, así que puedes cambiar la imagen, el joystick o los ajustes y ver
el resultado sin ir hasta la moto.

Lo que hace el tablero falso:

- responde al intercambio de claves (la clave pública RSA, `07 01 01`), para que REau llegue a "Transmitiendo";
- envía un latido, para que el vigilante de REau no termine la sesión, y confirma cada fotograma que decodifica (`09 06 55`, `09 04 55`);
- **graba el video** que REau envía (el flujo real H.264 de 526×300) para que puedas mirarlo;
- **pulsa los botones del joystick** (`09 00 0001 XX`) cuando se lo pides.

Lo que no hace: no es el tablero. No dibuja nada por sí mismo (el cristal redondo y el círculo que el tablero pone sobre la imagen se
dibujan después, con `frames --mask`, a partir de números medidos), no juzga colores, brillo ni cómo reacciona el firmware real, y se
salta la parte del Wi-Fi (unirse a `RE_xxxx`, la contraseña guardada, la unión automática). Lo que resuelvas aquí todavía necesita
una salida, o un minuto en la moto, para confirmarse.

## Qué necesitas

- Un computador y el teléfono **en la misma red Wi-Fi** (el router no debe aislar a los clientes; las redes de invitados suelen hacerlo).
- El teléfono con la depuración USB activada, conectado por `adb` y **desbloqueado** (un teléfono bloqueado muestra la pantalla en
  negro e ignora los toques).
- JDK 21 y el Android SDK, como para cualquier compilación de REau (mira el README).
- Python 3.9 o más nuevo, y `ffmpeg` (`brew install ffmpeg`) para mirar el video grabado.
- Android Auto en el teléfono con su "servidor de unidad principal" de desarrollador disponible, como para una salida normal. En la
  edición Lite, REau abre sola los ajustes de Android Auto la primera vez; toca ⋮ e "Iniciar servidor de unidad principal".

## Inicio rápido

Desde la raíz del repositorio, en dos terminales.

```
cd scripts/emu
make setup          # una vez: un entorno de Python con los dos paquetes de requirements.txt
make install        # el build de debug de la edición Lite en el teléfono (el que lleva el gancho de pruebas)
```

Terminal 1, déjala corriendo:

```
make dash           # el tablero falso; imprime "phone at <dirección>" cuando REau lo alcanza
```

Terminal 2:

```
make phone-host     # le dice a la app de debug del teléfono que use este computador como tablero
make start          # enciende REau (o toca Encender en el teléfono)
make button B=left  # pulsa un botón del joystick; mira la lista de abajo
make frames         # corta el video grabado en imágenes PNG con el cristal redondo y el círculo dibujados encima
make phone-clear    # de vuelta al tablero real: HAZLO SIEMPRE al terminar
```

`make help` repite esta lista. Las variables que quizá quieras: `APP` (el id de la app, `com.reau.app.lite` por defecto; la edición
completa es `com.reau.app`, pero aquí se prueba la Lite), `IP` (la dirección de este computador, cuando se equivoca al adivinarla),
`OUT` (dónde va el video) y `B` (el botón).

macOS pregunta una vez si Python puede aceptar conexiones entrantes: permítelo, o el teléfono nunca llegará al tablero falso.

## Qué hace `make phone-host`

Un build de debug de REau lee un archivo, `lan_dash_host.txt`, en su propia carpeta externa del teléfono:

```
/sdcard/Android/data/com.reau.app.lite/files/lan_dash_host.txt      una línea: una dirección IPv4
```

Mientras ese archivo tenga una dirección, REau no se une al Wi-Fi de la moto: envía los paquetes de control a esa dirección por UDP
2000 y el video por UDP 5000, y escucha en 2002, exactamente como con el tablero en 192.168.1.1. `make phone-host` escribe el archivo
(con `adb`) y `make phone-clear` lo borra. El registro de la salida lo dice cuando está en uso
(`test dash on the local network: <dirección>`), y un **build de release nunca lee el archivo**. El código está en
`app/src/main/java/com/reau/app/service/LanTestDash.kt`, probado por `LanTestDashTest`.

El archivo se lee al encender REau, así que un cambio de dirección (o `phone-clear`) surte efecto la próxima vez que toques Encender.

Sin `make`, lo mismo a mano:

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python3 fake_dash.py run --out fake_dash_out
.venv/bin/python3 fake_dash.py phone-host                 # o: phone-host 192.168.0.13 / phone-host clear
.venv/bin/python3 fake_dash.py button left
.venv/bin/python3 fake_dash.py frames fake_dash_out/dash-<hora>.h264 --out fake_dash_frames --fps 0.5 --mask
```

## Los botones

`make button B=<nombre>`, con los nombres de abajo, o un código directo (`B=0x13`). El tablero envía códigos distintos en sus dos modos:

| Nombre | Código | Para qué lo envía el tablero |
|---|---|---|
| `left`, `right`, `down`, `click` | 0x14, 0x13, 0x15, 0x18 | el joystick en el modo **mapa** del tablero (alejar/acercar, abajo, el centro) |
| `prev`, `next`, `vol-up`, `vol-down`, `play` | 0x0A, 0x09, 0x06, 0x07, 0x05 | el joystick en el modo **multimedia** del tablero |
| `back` | 0x12 | el botón de atrás (dos veces en menos de 0,7 s es el menú de apps) |

Lo que REau hace con cada uno está en la página del Joystick de la app. Las cuatro flechas mueven el foco de Android Auto; "Usar las
cuatro flechas" las pone. En el menú de apps el primer foco está en **Salir**: REau rechaza un Confirmar ahí (la imagen queda en blanco hasta volver a abrir el menú).

## Mirar la imagen

La grabación es el flujo que habría recibido el tablero: 526×300, H.264 sin contenedor, un archivo por cada ejecución de `make dash`
(`fake_dash_out/dash-<hora>.h264`). `make frames` corta el más reciente en `fake_dash_frames/frame-0001.png`, ... cada dos segundos,
y dibuja sobre cada uno:

- el **cristal redondo**, de 526 px de ancho, que oculta las dos esquinas de arriba (`DashGlass`);
- el **círculo propio del tablero**, de 120 px, abajo a la izquierda, que cubre parte de la imagen (`DashMask`).

Los dos son los números medidos en un tablero real, copiados en `fake_dash.py` (`GLASS`, `RING`); si cambian en la app, cámbialos
también ahí. Para todo el flujo en una sola hoja: `ffmpeg -framerate 4 -i ARCHIVO -vf "fps=1/3,scale=263:150,tile=6x6" hoja.png`.

Consejos de la práctica:

- Un archivo `.h264` crudo no tiene reloj: dile a ffmpeg el ritmo real (`-framerate 4`, como hace `make frames`) o `fps=` contará
  mal los segundos.
- Decodifica desde el principio (como hace `make frames`). Saltar cerca del final del archivo (`-sseof`) cae en un fotograma sin sus
  parámetros y da una imagen negra o vieja.
- Una línea `error while decoding MB` o `cbp too large` de ffmpeg al principio es inofensiva: es el primer fotograma.
- Una notificación en el teléfono (un mensaje de chat, por ejemplo) aparece sobre la imagen de Android Auto, y por tanto en la grabación.
- Cambiar el DPI, los márgenes o el lado de la barra de apps reinicia la sesión de Android Auto: espera 10 a 15 segundos antes de
  mirar la imagen nueva.
- Para comparar ajustes, cambia uno a la vez en la pantalla "Pantalla de Android Auto" de la app, espera y corta los fotogramas; la
  vista previa de esa pantalla también dibuja el cristal y el círculo (el botón "Máscara").

## Cuando algo no funciona

| Síntoma | Causa probable |
|---|---|
| `make phone-host`: "adb sees no phone" | el cable o la depuración USB; `adb devices` debe listarlo como `device` |
| El teléfono no hace caso a los toques de `adb`; las capturas salen negras | está bloqueado; desbloquéalo (nunca le dejes un PIN a un script) |
| REau dice "Transmitiendo" pero `make dash` no imprime nada | el teléfono no escribe a este computador: `IP` equivocada, otra red, aislamiento de clientes, o rechazaste el aviso del cortafuegos de macOS |
| REau se queda esperando a Android Auto | el servidor de unidad principal está apagado: toca ⋮ e "Iniciar servidor de unidad principal" en los ajustes de Android Auto |
| REau no arranca, o nunca oye al tablero | otra REau, u otra app del tablero, tiene el UDP 2002: detenla |
| `make frames`: "has no video yet" | REau no se encendió contra el tablero falso; corre `make phone-host` y luego `make start` |
| En la moto REau nunca se une al tablero | no se corrió `make phone-clear`: el archivo sigue en el teléfono |

## Pruebas

```
make test                                     # el tablero falso contra el lado del teléfono del protocolo
./gradlew :app:testLiteDebugUnitTest --tests '*LanTestDashTest'
```

`test_fake_dash.py` hace de teléfono con la disposición de bytes de `DashCommands` y `DashAuth` (petición de autenticación, clave de
sesión RSA, video FU-A, botones) y comprueba lo que vuelve.

## Sobre el código

`fake_dash.py` está escrito a partir del código de protocolo de REau (`dash/protocol/`, `DashSession`, `DashAuth`; el formato K1G se
acredita en `NOTICE`). No copia el emulador de otro proyecto. El formato del paquete de control, en corto: el teléfono envía
`[largo][cuenta][4 ceros][02 01 00 05]["K1G "][seq]` seguido de TLV `[tipo][sub][largo:2][valor]`; el tablero responde con
`[largo][cuenta][4 ignorados]` seguido de TLV, al UDP 2002 del teléfono.
