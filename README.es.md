# REau

English (por defecto): [README.md](README.md) · Português (pt-BR): [README.pt-br.md](README.pt-br.md)

Aplicación Android que lleva el **Android Auto del propio teléfono** al tablero TFT de la moto, por el Wi-Fi del tablero, con la
pantalla del teléfono apagada. REau no dibuja ningún mapa: repite en el tablero lo que la aplicación de navegación (Waze,
Google Maps) dibuja en Android Auto.

> **Compatibilidad:** funciona con el **Tripper Dash**. REau es un proyecto independiente, sin relación con Royal Enfield, y
> ni ella lo respalda ni lo mantiene.

## Cómo funciona

```
App de navegación ──▶ el Android Auto del teléfono ──(video H.264 por 127.0.0.1)──▶ REau
                                                                                    │ decodifica, recorta, reduce
                                                                                    ▼
                                                                 codificador 526×300 ──RTP──▶ tablero de la moto
```

REau se presenta a Android Auto como la unidad principal de un coche, usando el servidor de unidad principal que el propio
Android Auto ofrece en el modo de desarrollador. Recibe el video, ajusta la imagen a la pantalla del tablero y la envía por el
Wi-Fi del tablero.

## Qué hace

- Muestra la pantalla de Android Auto en el tablero, con un ajuste regulable (uno para las apps y otro para el menú de apps).
- Envía al tablero la maniobra, la distancia, la hora de llegada y el tiempo que falta de la ruta.
- Envía también la música que suena, las llamadas y el clima, para las tarjetas del tablero.
- Usa el joystick del manillar para controlar Android Auto (mapa, menú, música, llamadas): mientras suena una llamada, la
  izquierda contesta y la derecha o el centro rechazan; durante una llamada, el centro cuelga y arriba y abajo cambian el volumen.
  Las cuatro flechas mueven el foco de Android Auto en dos dimensiones.
- Habla portugués, inglés y español: sigue el idioma del teléfono, y los ajustes tienen un selector.
- Ajusta la calidad del video según la distancia a la próxima maniobra y la velocidad.
- Opcional: muestra Android Auto en un navegador de la red local, protegido por un PIN.
- Guarda un registro de diagnóstico en el almacenamiento interno de la app (activado por defecto, con un interruptor en los
  ajustes), para analizarlo en el computador (`scripts/registro/`); nada sale del teléfono si no lo compartes. Grabar el video
  y las sesiones es opcional y viene apagado.

## Requisitos

- Un teléfono con Android 10 o más nuevo y **Android Auto** instalado.
- El modo de desarrollador de Android Auto activado, con el "servidor de unidad principal". En la edición completa, REau abre esa
  pantalla y enciende el servidor por sí sola cuando la accesibilidad de la app está activa; en la Lite, lo enciendes a mano.
- En Android 13 o más nuevo, para activar el servicio de accesibilidad (edición completa) primero hay que permitirlo en Ajustes ›
  Apps › REau › ⋮ › "Permitir ajustes restringidos": Android lo pide a cualquier app instalada fuera de Play Store, incluido el
  APK publicado.
- Un tablero compatible, con su Wi-Fi al alcance.

## Dos ediciones

- **Completa** (`com.reau.app`): la habitual. Usa un servicio de accesibilidad de Android para encender el servidor de Android
  Auto por sí sola y saber qué pantalla de Android Auto se muestra (el ajuste propio del menú de apps).
- **Lite** (`com.reau.app.lite`, "REau Lite", **la recomendada**): **sin** servicio de accesibilidad. Con Android Auto 17.4 o más
  nuevo enciendes el servidor de unidad principal a mano (se apaga al terminar la sesión, así que lo enciendes de nuevo cada vez),
  y no hay ajuste propio para el menú de apps. REau abre por sí sola los ajustes de Android Auto, y solo quedan dos toques
  (⋮ y "Iniciar servidor de unidad principal").

**Cuál usar: la Lite es la edición recomendada.** No pide ningún servicio de accesibilidad, así que nunca obtiene un control amplio
del teléfono y no choca con apps que se niegan a funcionar con la accesibilidad activa (las bancarias, por ejemplo). El precio es un
paso manual cada vez: enciendes tú el servidor de unidad principal de Android Auto. Elige la completa solo si quieres que REau haga
ese paso sola y que ajuste el menú de apps de Android Auto.

Las dos se instalan juntas en el mismo teléfono, pero no deben funcionar a la vez (compiten por el tablero).

## Inicio rápido

Hay un acceso directo en el icono de la app y un bloque en los Ajustes rápidos ("Encender REau") que abren REau y encienden la
proyección de una vez.

## Guías

- [guides/himalayan-450.es.md](guides/himalayan-450.es.md): instalar y poner a funcionar REau con una Himalayan 450, con los ajustes de imagen
  y de joystick que mejor resultado dieron.
- [guides/fork.es.md](guides/fork.es.md): cómo se trabaja en este repositorio (remoto, ramas, cómo traer cambios del proyecto original).
- [scripts/emu/FAKE_DASH.es.md](scripts/emu/FAKE_DASH.es.md): probar cambios sin la moto, con un tablero falso en el computador.

## Compilación

Con JDK 21 y el Android SDK instalados:

```
./gradlew assembleRelease               # los dos APK: app/build/outputs/apk/completa/release/ y .../lite/release/
./gradlew assembleCompletaRelease       # solo la edición completa (com.reau.app); assembleLiteRelease: solo la Lite
./gradlew :app:testDebugUnitTest        # pruebas unitarias
```

Las pruebas instrumentadas (`app/src/androidTest`) corren en un emulador, contra un Android Auto falso y un tablero falso.

Para probar un cambio sin la moto (la imagen, el joystick, los ajustes), un build de debug puede hablar con un tablero falso en tu
computador: mira [scripts/emu/FAKE_DASH.es.md](scripts/emu/FAKE_DASH.es.md).

Hay un APK publicado en la página de Releases del proyecto; para compilar el tuyo, Gradle tiene que encontrar el Android SDK
(`ANDROID_HOME`, o `sdk.dir` en `local.properties`), y `assembleRelease` firma con la clave de debug de Android, porque el
repositorio no trae la clave de firma del proyecto. Las Releases oficiales se firman con esa clave, guardada fuera del repositorio;
sin las variables de entorno `REAU_KEYSTORE`, `REAU_KEY_ALIAS`, `REAU_KEYSTORE_PASSWORD` y `REAU_KEY_PASSWORD`, un release compilado
localmente sale firmado con la clave de debug.

## Privacidad

REau no tiene cuenta, ni anuncios, ni recoge datos. La pantalla **"REau y tus datos"**, dentro de la app, dice qué se queda en el
teléfono, qué sale y por qué. Lo que sale del teléfono va al tablero y, solo con el servidor de red opcional encendido, a otros
dispositivos de tu red local; el único viaje a internet es el del clima, opcional (Open-Meteo).

## Seguridad

No manipules el teléfono mientras conduces. Usa el joystick del manillar, y solo cuando la moto esté en condiciones seguras.

## Historial de cambios

Todos los cambios importantes están en [CHANGELOG.md](CHANGELOG.md) (en portugués: [CHANGELOG.pt-br.md](CHANGELOG.pt-br.md)).

## Términos de uso

La app te pide aceptar los [términos de uso](TERMS_OF_USE.md) la primera vez que se abre (en portugués:
[TERMS_OF_USE.pt-br.md](TERMS_OF_USE.pt-br.md)); están al final de la pantalla **"REau y tus datos"**, junto a los créditos. Los términos
no se tradujeron al español: son un texto legal, y solo valen el inglés y el portugués.

## Licencia y créditos

REau es software libre bajo la **GNU Affero General Public License v3.0** ([LICENSE](LICENSE)). Incorpora código de otros proyectos
abiertos; el archivo [NOTICE](NOTICE) enumera cada uno, con su licencia y lo que se usó, y la app muestra los mismos créditos en la
pantalla **Créditos**, al final de **"REau y tus datos"**, donde también se da la dirección del código fuente de REau (la AGPL
pide que los usuarios de la app puedan obtenerlo).
