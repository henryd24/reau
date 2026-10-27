# REau con una Himalayan 450 (tablero Tripper)

English: [himalayan-450.md](himalayan-450.md)

Guía en español, escrita con un Samsung S25 Ultra (Android 17, Android Auto 17.9) y una Himalayan 450. Lo que cambia en otro
teléfono o con otro firmware, se dice donde corresponde. Lo que no se pudo comprobar, está marcado como **sin confirmar**.

## 1. Qué instalar

La edición **Lite** (`com.reau.app.lite`) es la recomendada: no pide servicio de accesibilidad y solo exige un paso manual
por sesión (dos toques). Instálala desde la página de Releases, o compílala:

```
./gradlew assembleLiteRelease
adb install -r app/build/outputs/apk/lite/release/*.apk
```

Para compilar necesitas JDK 21 y el Android SDK (mira el [README](../README.es.md)). Si solo quieres una versión de prueba,
`./gradlew installLiteDebug` la deja instalada directamente.

## 2. Preparar Android Auto (una vez)

REau necesita el **servidor de unidad principal** que Android Auto ofrece en su modo de desarrollador.

1. En el teléfono: Ajustes › Android Auto, baja hasta el final y toca **"Versión" unas diez veces**; confirma.
2. Aparece el menú **⋮** con la configuración para desarrolladores.
3. En ese menú está **"Iniciar servidor de unidad principal"**. Es lo que hay que tocar cada vez que sales a rodar (el servidor se
   apaga al terminar la sesión y tras reiniciar el teléfono).

Si el menú no aparece, el modo de desarrollador no quedó activo: repite los diez toques.

## 3. La primera vez con la moto

1. Enciende la moto y deja el teléfono cerca del tablero.
2. Abre REau, acepta los términos y concede los permisos que pida (la pantalla **Permisos** dice cuál falta y para qué sirve cada
   uno; la ubicación se usa solo para ver la lista de Wi-Fi y encontrar el nombre completo del tablero).
3. Toca **Encender**. En la Lite, REau abre sola los ajustes de Android Auto: toca **⋮ › Iniciar servidor de unidad principal** y
   vuelve a REau.
4. Android puede preguntar si REau puede conectarse al Wi-Fi del tablero (`RE_xxxx_yymmdd`): toca **Conectar**.
5. Cuando la app diga **Transmitiendo**, el tablero muestra Android Auto.

Para las siguientes veces hay un acceso directo en el icono de la app y un bloque de Ajustes rápidos, **Encender REau**: abren REau
y encienden la proyección de una vez.

## 4. La imagen: qué se ve y qué no

El cristal del tablero es redondo y corta las dos esquinas de arriba. Además, el propio tablero dibuja un **círculo con los
íconos naranja** sobre la parte baja izquierda de la imagen, y REau no puede apagarlo. Por eso, con Android Auto en su
disposición normal (botones a la izquierda), el micrófono y el botón del lanzador de apps quedan tapados.

En la pantalla **Pantalla de Android Auto** (acceso en la pantalla principal) hay un botón **Máscara** que dibuja el cristal y el
círculo sobre la vista previa, para ver qué llega al cristal sin ir a la moto.

El ajuste que mejor funcionó:

| Ajuste | Valor | Por qué |
|---|---|---|
| Modo | **Imagen entera** | no se pierde ningún borde: se ve la búsqueda y todo el riel |
| DPI de Android Auto | 180 (o 240 si quieres texto más grande) | con 240 Android Auto muestra menos cosas a la vez |
| **Botones de apps a la derecha** | activado | el riel pasa a la derecha, lejos del círculo del tablero |
| Mover en vertical | a gusto | pega la imagen al borde de abajo |

"Llenar el domo" con los botones a la derecha da una imagen bastante más grande y también deja el riel entero a la vista, pero
corta la barra de búsqueda por la izquierda. Cambiar el DPI, los márgenes o el lado de los botones reinicia la sesión de Android
Auto: espera unos segundos.

**Sin confirmar en la moto:** estas comparaciones se hicieron con un tablero falso y las medidas del código; el resultado final se
ve en el tablero real.

## 5. El joystick

En la pantalla **Joystick del tablero** hay un botón, **Usar las cuatro flechas**, que pone arriba, abajo, izquierda y derecha para
mover el foco de Android Auto en dos dimensiones y el centro como **Confirmar**. Con eso:

- **Menú de apps:** dos toques rápidos (menos de 0,7 s) en **Atrás**.
- **Atrás:** un toque en Atrás.
- **En el modo mapa del tablero**, arriba es del propio tablero (pregunta si quieres salir de la navegación) y el centro cambia a
  multimedia; por eso ahí solo hay izquierda, derecha y abajo.
- **Cuidado con "Salir":** al abrir el menú de apps, el primer foco está en **Salir**. Si pulsas Confirmar justo entonces, cierras
  Android Auto (REau lo vuelve a abrir en un segundo, pero se pierde la ruta en pantalla). Mueve el foco antes de confirmar.

"Restablecer valores" en la misma pantalla vuelve al joystick de antes.

## 6. Si algo no funciona

| Qué pasa | Qué probar |
|---|---|
| "Android Auto no acepta la conexión" | el servidor está apagado: ⋮ › "Iniciar servidor de unidad principal"; tras reiniciar el teléfono hay que repetirlo |
| El tablero se queda con el último cuadro o negro | fuerza la detención de Android Auto y vuelve a encender REau |
| No conecta con el tablero | VPN activa (deja a REau fuera del túnel), ahorro de batería, o la otra edición de REau encendida: no deben funcionar a la vez |
| Android Auto se cierra con la pantalla apagada | **sin confirmar**: dos veces en los registros la sesión terminó justo al apagarse la pantalla; si te pasa, anota la hora y comparte los registros |
| Cambié el ajuste y se ve mal | "Restablecer al valor por defecto" en la pantalla de Android Auto |

**Compartir los registros** (para analizarlos en el computador): en los Ajustes, sección **Depuración**, hay un botón de
compartir. El registro no lleva tu ubicación; `scripts/registro/` tiene herramientas para leerlo.

## 7. Probar sin la moto

Si quieres cambiar algo y ver el resultado sin ir hasta la moto, hay un tablero falso para el computador:
[scripts/emu/FAKE_DASH.es.md](../scripts/emu/FAKE_DASH.es.md).

## Seguridad

No manipules el teléfono mientras conduces. Usa el joystick del manillar, y solo cuando la moto esté en condiciones seguras.
