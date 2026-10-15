# Git Bash + GitHub: laboratorio sicurezza, CI/CD e rollback

Ambiente didattico per Windows e Git Bash. Python 3.12, Bandit 1.9.4 e GitHub Actions.
Non servono Docker, server, token inseriti nel codice o servizi a pagamento aggiuntivi per il test locale.
I consumi di GitHub Actions dipendono dal piano e dalla disponibilità di minuti del tuo account.

## Cosa succede

| Stato | Gate | Rilascio simulato |
| --- | --- | --- |
| Commit iniziale sicuro | Passa | Crea uno ZIP del codice applicativo |
| Commit con shell=True e input esterno | Fallisce: Bandit B602 | Bloccato; il puntatore locale precedente resta invariato |
| Nuovo commit creato con git revert | Passa | Crea un nuovo ZIP contenente il codice ripristinato |

Il rollback viene richiesto manualmente con Git; il gate e il packaging successivi sono automatici.
Non è configurato un bot che riscrive o ripristina il repository automaticamente.

## 1. Prepara la cartella e Python

Estrai lo ZIP. Apri la cartella `git-security-lab` in Esplora file e seleziona **Open Git Bash here**
(su Windows 11 può essere sotto **Mostra altre opzioni**).
I comandi successivi partono da questa cartella, quella contenente questo README.

```bash
pwd
ls -la
git --version
python --version
```

Serve Python 3.10 o successivo; la CI usa 3.12. Se Python manca, installa Python dal sito ufficiale
https://www.python.org/downloads/windows/ e abilita l'aggiunta al PATH, poi riapri Git Bash.
Se funziona `py -3.12` ma non `python`, usa `py -3.12 -m venv .venv` al posto della prima riga seguente.

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
python app/report.py Andrea
bash scripts/validate.sh
```

Risultato: `Report per: Andrea`, quattro test superati e `GATE PASSATO`.
Su Linux la riga di attivazione è `source .venv/bin/activate`.
Quando riapri Git Bash, rientra nella cartella e riattiva il virtual environment.

## 2. Inizializza Git e crea il punto sicuro

Sostituisci nome ed email con i tuoi; per l'email puoi usare quella privata noreply indicata nelle impostazioni GitHub.
Questi comandi configurano l'autore solo per questa repository, senza cambiare gli altri progetti.

```bash
git init -b main
git config user.name "Nome Cognome"
git config user.email "EMAIL_ASSOCIATA_A_GITHUB"
git status
git add .
git diff --cached --stat
git commit -m "lab: baseline sicura con gate e pipeline"
git tag baseline-safe
bash scripts/pipeline.sh
cat dist/current.json
```

`dist/current.json` identifica il commit della versione simulata corrente.
Gli ZIP sono in `dist/releases/`. La cartella dist è ignorata da Git.
La pipeline locale richiede una working tree pulita: prima di creare un pacchetto salva le modifiche con un commit.
Il controllo evita di validare file modificati e poi archiviare una versione differente da HEAD.

## 3. Collega la repository a GitHub

In GitHub crea una nuova repository **vuota** chiamata `git-security-lab`, preferibilmente privata.
Non aggiungere README, .gitignore o licenza: sono già presenti localmente.
Sostituisci `TUO_USERNAME` nei comandi. L'autenticazione HTTPS configurata in Git Bash sarà riutilizzata.

```bash
git remote add origin https://github.com/TUO_USERNAME/git-security-lab.git
git remote -v
git push -u origin main
git push origin baseline-safe
```

Apri **Actions → Security lab** sulla repository e attendi l'esito.
Il job `validation-gate` deve passare; `simulated-release` genera un artifact scaricabile dalla pagina della run.
Il file `.github/workflows/ci.yml` definisce questi due job.

## 4. Crea un branch e introduci la vulnerabilità

```bash
git switch -c test/unsafe-script
cp examples/report_unsafe.py.txt app/report.py
git status
git diff -- app/report.py
bash scripts/validate.sh
echo $?
```

Il gate DEVE fallire, normalmente con exit code 1. Bandit deve indicare **B602**.
Il comando `echo $?` va eseguito subito dopo il controllo per leggerne il risultato.
La vulnerabilità consiste nel passare l'input a `subprocess.run(..., shell=True)`:
la shell può interpretarlo come parte di un comando. Per la prova basta la scansione statica;
non occorre eseguire lo script vulnerabile.

Ora salva e invia intenzionalmente il commit difettoso nel branch di test:

```bash
git add app/report.py
git diff --cached -- app/report.py
git commit -m "lab: introduce command injection per testare il gate"
git push -u origin test/unsafe-script
bash scripts/pipeline.sh
cat dist/current.json
```

La pipeline locale fallisce prima del packaging; il puntatore resta sul commit sicuro precedente.
In GitHub Actions il gate diventa rosso e `simulated-release` risulta **Skipped**.
Il fallimento locale non impedisce il commit o il push: questo laboratorio non installa hook Git.
Attendi di vedere la run rossa prima di procedere, per distinguere chiaramente i tre stati.

## 5. Esegui il rollback con git revert

```bash
git status
git log --oneline --decorate -5
git show --stat HEAD
git revert --no-edit HEAD
bash scripts/pipeline.sh
git push
git log --oneline --graph --decorate --all
git diff baseline-safe HEAD -- app/report.py
cat dist/current.json
```

`git revert --no-edit HEAD` è corretto qui perché HEAD è ancora il commit vulnerabile appena creato.
Se hai fatto altri commit, individua quello vulnerabile con `git log` ed esegui invece `git revert --no-edit SHA_DEL_COMMIT`.
Se ci sono modifiche non salvate, fermati e controlla `git status` prima del revert.

Git crea un nuovo commit che annulla il difetto, mantenendo lo storico.
Il comando `git diff baseline-safe HEAD -- app/report.py` non deve stampare differenze.
Il codice coincide con la baseline, ma il commit è nuovo: per questo anche lo ZIP ha un nuovo identificativo.
Il gate e il rilascio simulato su GitHub tornano verdi dopo il push.

Il rollback agisce sul branch di test: `main` è rimasto sicuro per tutta la prova.
Puoi lasciare il branch come esercizio o aprire una pull request verso `main` per vedere i controlli sulla PR.

## 6. Altri comandi da provare

| Comando | Scopo |
| --- | --- |
| `git status` | File modificati, staged e branch corrente |
| `git diff` | Modifiche non ancora aggiunte allo staging |
| `git diff --cached` | Modifiche che entreranno nel prossimo commit |
| `git restore --staged app/report.py` | Togli il file dallo staging, conservando le modifiche |
| `git show baseline-safe:app/report.py` | Leggi la vecchia versione senza cambiare i file |
| `git branch -a` | Branch locali e remoti conosciuti |
| `git fetch origin` | Aggiorna i riferimenti remoti senza unire modifiche |
| `git log --oneline --graph --decorate --all` | Visualizza la storia dei commit |
| `git switch main` | Torna al branch principale |

Esercizio separato, da fare a working tree pulita: ripristino di una modifica NON committata.

```bash
printf '\n# Modifica temporanea\n' >> app/report.py
git diff
git restore -- app/report.py
git status
```

Questo `restore` elimina esclusivamente la modifica non committata del file indicato.
Per annullare commit già condivisi, usa `revert`: non occorrono force push o reset --hard.

## Come funziona il gate

1. Bandit analizza `app/` e blocca finding con severità e confidenza almeno medium.
2. Solo se la scansione passa, esegue quattro test Python.
3. Solo se l'intero gate passa, la pipeline può creare il pacchetto.

L'esempio vulnerabile in `examples/` è intenzionalmente un file `.txt` fuori da `app/`.
Serve come materiale didattico; viene analizzato quando lo copi in `app/report.py`.
Il pacchetto di rilascio contiene solo `app/`, non gli esempi vulnerabili.
I finding low non bloccano questo gate. Bandit non è una prova di assenza di tutte le vulnerabilità,
né un audit delle dipendenze. I file di pipeline non fanno parte del target Bandit di questo esercizio.

## CI, blocco dei merge e CD: distinzioni

- Il workflow esegue il gate su push, pull request e avvio manuale.
- Il job di rilascio parte solo sui push e solo dopo il successo del gate.
- Il rilascio è simulato: crea ZIP e manifest. Nessun sito, VM o servizio viene aggiornato.
- Su GitHub ogni run parte da un runner nuovo; gli artifact precedenti restano nelle rispettive run
  fino alla scadenza configurata. `dist/current.json` persiste tra esecuzioni solo sulla tua macchina locale.
- Un gate rosso da solo NON vieta il merge o i push diretti: servono regole di protezione del branch.
  Se il tuo piano le supporta, proteggi `main`, richiedi una pull request e rendi obbligatorio
  il controllo `validation-gate`, senza bypass. La disponibilità per repository private dipende dal piano.
- Un rollback di un'applicazione realmente distribuita richiederebbe anche il ripristino/redeploy sul server:
  `git revert` da solo modifica il codice, non un ambiente esterno.

## File principali

| File | Funzione |
| --- | --- |
| `app/report.py` | Applicazione inizialmente sicura |
| `examples/report_unsafe.py.txt` | Variante vulnerabile da copiare nel branch di test |
| `tests/test_report.py` | Test funzionali e gestione dei caratteri speciali |
| `scripts/validate.sh` | Gate usato sia in locale sia nella CI |
| `scripts/pipeline.sh` | Gate + packaging locale |
| `scripts/package_release.py` | Crea archivio e aggiorna il manifest della simulazione |
| `.github/workflows/ci.yml` | Automazione GitHub Actions |

## Riferimenti

- Git revert: https://git-scm.com/docs/git-revert
- Bandit B602: https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html
- GitHub Actions e Python: https://docs.github.com/en/actions/tutorials/build-and-test-code/python
- Artifact: https://docs.github.com/en/actions/tutorials/store-and-share-data
- Protezione branch: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
