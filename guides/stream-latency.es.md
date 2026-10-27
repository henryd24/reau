# Probar la frecuencia del video y medir el retraso

English: [stream-latency.md](stream-latency.md)

En el tablero el mapa se mueve a saltos: REau envía 4 imágenes por segundo (perfil A) y solo 2 (perfil B) cuando la próxima maniobra de
la ruta está a más de 1 km o la velocidad pasa de unos 65 km/h. Esos dos valores, 4 y 2 fps con 100 kbps por cada cuadro por segundo,
son los que se sabe que funcionan en este tablero: con más, el video "se atrasaba a velocidad" (el tablero parece acumular imágenes, y
entonces el retraso crece en vez de bajar). Esta guía sirve para probar otros valores en la moto y para medir el retraso, de modo que
la decisión se tome con números.

No cambia nada si tú no lo cambias: los valores por defecto siguen siendo 4 / 2 fps y "Frecuencia menor".

## Qué se puede cambiar (Ajustes › Perfiles de video)

| Ajuste | Por defecto | Qué hace |
|---|---|---|
| **Frecuencia del perfil A** (experimental) | 4 fps | la frecuencia mientras hay una maniobra cerca y la velocidad es baja; de 4 a 10 en pasos de 2. El bitrate la sigue: 100 kbps por cada cuadro por segundo (nunca más de 1 Mbps, que hacía trabarse al tablero) |
| **Frecuencia del perfil B** | 2 fps | la frecuencia lejos de una maniobra y a velocidad; de 2 hasta la del perfil A |
| **Cuando los dos perfiles no coinciden** | Frecuencia menor | el perfil de maniobra y el de velocidad suelen pedir frecuencias distintas. *Frecuencia menor* usa B si cualquiera lo pide (la imagen más liviana); *Frecuencia mayor* usa A si cualquiera lo pide (la más fluida). Se aplica de inmediato |

Las frecuencias abren un flujo nuevo (la imagen se congela un segundo); la política se lee todo el tiempo.

Un buen orden para probarlas, un paso a la vez, primero con la moto parada y luego en un trayecto corto:

1. **Frecuencia mayor** con 4 / 2 fps. No cuesta bits: solo mantiene el perfil A cuando cualquiera de los dos perfiles lo permite.
2. **6 / 4 fps**, luego **8 / 4 fps**, con *Frecuencia mayor* o *Frecuencia menor*.
3. Al primer signo de que la imagen se queda atrás (la flecha de la maniobra llega tarde, la imagen salta tras una pausa, el tablero se
   pone negro), vuelve un paso atrás. 4 / 2 fps siempre es seguro.

## Medir el retraso con el reloj del teléfono

El retraso es difícil de juzgar a ojo. REau puede escribir el reloj del teléfono, con milésimas, sobre el video del tablero, y la
pantalla del propio teléfono muestra el mismo reloj en vivo; filmados juntos, la diferencia entre los dos es lo que tarda la imagen
en llegar al tablero.

1. Abre **Pantalla de Android Auto** (el acceso de la pantalla principal) y baja hasta el final: **Reloj del teléfono sobre el video**. Actívalo.
2. Pon el cuadro sobre la imagen: con "Imagen entera", el cuadro en su lugar por defecto queda encima, fuera de la vista previa. Sube
   **Vertical (Y)** a unos 90 px (y **Horizontal (X)** a gusto). El mismo cuadro, con el mismo reloj, se dibuja en la vista previa de esa pantalla.
3. Deja esa pantalla abierta en el teléfono, con la proyección encendida, y pon el teléfono **al lado del tablero**.
4. **Filma los dos en una sola toma**, en cámara lenta o a 60 fps si la cámara lo permite, de 10 a 20 segundos. Hazlo **con la moto
   parada, o con otra persona filmando**: nunca filmes mientras conduces.
5. Pausa el video en varios fotogramas y lee los dos relojes. El del teléfono es la hora actual; el del tablero es la hora en que se
   compuso el fotograma. *Retraso = reloj del teléfono − reloj del tablero.* La pantalla del teléfono suma unas decenas de
   milisegundos, poco al lado de lo del tablero.
6. Repite con los ajustes que quieras comparar (4 / 2, 6 / 4, 8 / 4), parado y, si se puede hacer con seguridad, con el mapa en
   movimiento (acercando con el joystick).
7. Apaga el reloj al terminar: es una ayuda de prueba, no para rodar.

Para leer el video después: `ffmpeg -i video.mp4 -vf fps=10 frames/f-%04d.png`, y mira los fotogramas donde los dos relojes se lean bien.

## Probarlo sin la moto

El tablero falso ([scripts/emu/FAKE_DASH.es.md](../scripts/emu/FAKE_DASH.es.md)) graba el flujo y muestra que las frecuencias cambian de
verdad (la línea de 5 segundos del registro dice `target=8 sent=8.0`, y el tablero confirma lo mismo). No puede decir cómo se las
arregla el tablero real: para eso está el reloj filmado.

## Dejarlo como estaba

Perfil A 4 fps, perfil B 2 fps, *Frecuencia menor*, reloj apagado. El grupo de Perfiles de video no tiene botón de restablecer; usa
los botones − y +.
