# Cómo está montado este fork

Este repositorio es un fork de [Murkiriel/reau](https://github.com/Murkiriel/reau) en `henryd24/reau`. El proyecto original es del
autor: aquí se trabaja sin tocarlo.

## Remotos

| Remoto | Dirección | Para qué |
|---|---|---|
| `origin` | `https://github.com/Murkiriel/reau.git` | el proyecto del autor: **solo se lee** (fetch). No se empuja nada ahí |
| `mine` | `git@github.com:henryd24/reau.git` | este fork: aquí sí se empuja, y solo cuando se pide |

`git config remote.pushDefault` está en `mine`, para que un `git push` sin destino vaya al fork y nunca al autor. Para comprobarlo:

```
git remote -v
git config remote.pushDefault        # debe decir: mine
```

## Ramas

- `main`: la base del fork. Tiene lo del autor más lo que se ha integrado: el español, los pasos manuales que se quitaron (abrir
  los ajustes de Android Auto sola, inicio rápido, el wrapper oficial de Gradle).
- `feat/fewer-manual-steps` y `feat/spanish-translation`: ya están dentro de `main`; se pueden borrar cuando se quiera.
- `feat/lan-test-dash`: el tablero falso, las cuatro flechas del joystick, los botones de apps a la derecha y la documentación en español. Todavía
  no está en `main`.

## Trabajar en un cambio

```
git switch -c feat/lo-que-sea main      # una rama por cambio
# ... cambios, pruebas ...
git commit                              # los commits son locales
git push mine feat/lo-que-sea           # solo cuando se decida subirlo, y siempre a "mine"
```

Antes de dar un cambio por terminado: `./gradlew detekt lintLiteDebug lintCompletaDebug testLiteDebugUnitTest testCompletaDebugUnitTest`.
El test `DashSessionReplacedSessionTest` falla a veces cuando la máquina está muy cargada (usa sockets reales y esperas cortas) y pasa
cuando se corre solo; si es el único que falla, repite ese test aislado.

## Traer los cambios del autor

```
git fetch origin
git switch main
git merge origin/main                   # si hay conflictos, resolverlos y commitear
git push mine main                      # solo cuando se decida
```

Las ramas de trabajo se actualizan después con `git merge main` (o `git rebase main` si no se han subido todavía).

## Un pull request al autor

No se ha abierto ninguno. Si algún día se quiere ofrecer un cambio al proyecto original, debe ir en su propia rama, que parta de
`origin/main` y lleve solo ese cambio, y abrirse desde el fork en GitHub; nunca empujando a `origin`. El autor decide si lo acepta.

## Cosas que no deben subirse

- Los registros (`*.log`, `logs/`) y los videos grabados (`*.h264`): pueden llevar el nombre del Wi-Fi del tablero o posiciones. Ya están en
  `.gitignore`.
- Las claves de firma (`*.jks`, `signing.properties`).
- Los mensajes de commit no llevan líneas `Co-Authored-By`.
