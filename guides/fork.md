# Working on this repository

Español: [fork.es.md](fork.es.md)

This repository continues [Murkiriel/reau](https://github.com/Murkiriel/reau) (REau, AGPL-3.0) as an independent line of
work: its `main` is the reference, and no remote for the original project is configured. The credit stays in the
[NOTICE](../NOTICE) and on the app's Credits screen.

## Remote and branches

- `origin` is this repository's own hosting; it is the only remote. Check it with `git remote -v`.
- `main` is the base. Every change goes in its own branch cut from `main` (`feat/...`, `fix/...`, `docs/...`) and is merged
  back with a merge commit once its checks pass.
- Commits stay local until someone decides to publish them: `git push origin <branch>`.

## Working on a change

```
git switch -c feat/what-it-does main
# ... change, try it ...
git commit
git switch main && git merge --no-ff feat/what-it-does
```

Before calling a change done:

```
./gradlew detekt lintLiteDebug lintCompletaDebug testLiteDebugUnitTest testCompletaDebugUnitTest
```

`DashSessionReplacedSessionTest` sometimes fails when the machine is heavily loaded (it uses real sockets and short waits) and
passes when run alone; if it is the only failure, run that test on its own.

To try a change without the bike, see [scripts/emu/FAKE_DASH.md](../scripts/emu/FAKE_DASH.md).

## Taking changes from the original project

Nothing is configured for it. When a change of the original project is wanted, add its address as a temporary remote, bring
what is needed and remove it again:

```
git remote add upstream https://github.com/Murkiriel/reau.git
git fetch upstream
git cherry-pick <commit>        # or: git merge upstream/main (expect conflicts: the two lines have diverged)
git remote remove upstream
```

## A pull request to the original project

It is not part of the workflow. If one is ever wanted, it goes in its own branch cut from the original's `main`, with only that
change, and is opened from the fork on GitHub.

## What never goes in the repository

- Logs (`*.log`, `logs/`) and recorded video (`*.h264`): they may carry the dash's Wi-Fi name or positions. They are in `.gitignore`.
- Signing keys (`*.jks`, `signing.properties`).

## Documentation

English is the base language. Every new document gets a Spanish version next to it, with the `.es.md` suffix (`fork.md` and
`fork.es.md`), and the two link to each other; the Portuguese (`.pt-br.md`) texts are the ones the original project already had.
Folders and files are named in English, whatever the language of what they hold.
