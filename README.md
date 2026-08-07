# sigma-snapshots

Capture quotidienne automatique (GitHub Actions, 18h45 UTC jours ouvrés) des
données de séance de 5 bourses africaines dont les API ne servent que le jour
courant :

| Fichier | Bourse | Contenu |
|---|---|---|
| `ngx.json` | Lagos (NGX) | OHLC + volumes + montants du jour |
| `zse.json` | Harare (ZSE) | cours + volumes + montants (cents ZWG) |
| `bse_domestic.json` / `bse_foreign.json` | Gaborone (BSE) | cours + volumes + montants |
| `use.json` | Kampala (USE) | cours + volumes (sans date : celle du dossier fait foi) |
| `mse.html` | Blantyre (MSE) | table officielle du jour |

Les réponses sont archivées **brutes** dans `snapshots/AAAA-MM-JJ/` — le
parsing vit dans la plateforme Sigma Finance locale, qui importe l'arriéré à
chaque mise à jour (`scripts/import_cloud_snapshots.py`).

Ces données sont publiques (cours de bourse officiels). `meta.json` journalise
chaque capture (heure UTC, succès/échecs).
