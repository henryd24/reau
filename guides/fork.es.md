# Trabajar en este repositorio

English: [fork.md](fork.md)

Este repositorio continúa [Murkiriel/reau](https://github.com/Murkiriel/reau) (REau, AGPL-3.0) como una línea de trabajo independiente: su
`main` es la referencia, y no hay configurado ningún remoto del proyecto original. El crédito se mantiene en el
[NOTICE](../NOTICE) y en la pantalla de Créditos de la app.

## Remoto y ramas

- `origin` es el alojamiento propio de este repositorio; es el único remoto. Se comprueba con `git remote -v`.
- `main` es la base. Cada cambio va en su propia rama, cortada desde `main` (`feat/...`, `fix/...`, `docs/...`), y se integra de
  vuelta con un commit de unión cuando pasan sus comprobaciones.
- Los commits se quedan locales hasta que alguien decide publicarlos: `git push origin <rama>`.

## Trabajar en un cambio

```
git switch -c feat/lo-que-hace main
# ... cambios, pruebas ...
git commit
git switch main && git merge --no-ff feat/lo-que-hace
```

Antes de dar un cambio por terminado:

```
./gradlew detekt lintLiteDebug lintCompletaDebug testLiteDebugUnitTest testCompletaDebugUnitTest
```

`DashSessionReplacedSessionTest` falla a veces cuando la máquina está muy cargada (usa sockets reales y esperas cortas) y pasa cuando se
corre solo; si es el único que falla, se repite ese test aislado.

Para probar un cambio sin la moto, mira [scripts/emu/FAKE_DASH.es.md](../scripts/emu/FAKE_DASH.es.md).

## Traer cambios del proyecto original

No hay nada configurado para eso. Cuando se quiere un cambio del proyecto original, se añade su dirección como remoto temporal, se trae
lo necesario y se vuelve a quitar:

```
git remote add upstream https://github.com/Murkiriel/reau.git
git fetch upstream
git cherry-pick <commit>        # o: git merge upstream/main (habrá conflictos: las dos líneas se han separado)
git remote remove upstream
```

## Un pull request al proyecto original

No forma parte del flujo. Si alguna vez se quiere uno, va en su propia rama, cortada desde el `main` del original y con solo ese cambio,
y se abre desde el fork en GitHub.

## Lo que nunca entra en el repositorio

- Los registros (`*.log`, `logs/`) y el video grabado (`*.h264`): pueden llevar el nombre del Wi-Fi del tablero o posiciones. Están en `.gitignore`.
- Las claves de firma (`*.jks`, `signing.properties`).

## Documentación

El inglés es el idioma base. Cada documento nuevo lleva al lado una versión en español, con el sufijo `.es.md` (`fork.md` y
`fork.es.md`), y las dos se enlazan entre sí; los textos en portugués (`.pt-br.md`) son los que ya tenía el proyecto original.
Las carpetas y los archivos se nombran en inglés, sea cual sea el idioma de lo que contienen.
