# Verifica del progetto consegnato

Eseguita in una repository Git temporanea con Bash, Python 3.12 e Bandit 1.9.4.

| Prova | Risultato |
| --- | --- |
| Baseline sicura: scansione e 4 test | PASS |
| Creazione pacchetto e manifest del commit | PASS |
| Copia della variante vulnerabile e commit | PASS |
| Rilevamento B602 e blocco del packaging | PASS |
| Manifest precedente invariato dopo il blocco | PASS |
| git revert del commit vulnerabile | PASS |
| Scansione e 4 test dopo rollback | PASS |
| Codice archiviato identico alla baseline | PASS |
| Blocco packaging con working tree modificata | PASS |

I test sono stati eseguiti su Linux, non sul tuo PC Windows.
Il workflow GitHub Actions è predisposto ma non è stato eseguito su una repository remota.
La guida README contiene i passaggi per creare la repository e osservare le run reali.
