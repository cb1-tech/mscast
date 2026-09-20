# MSCAST ERP - folder guide

Two folders, one purpose each.

| Folder | What is in it |
|---|---|
| **ERP Plan** | The documents. One current version of each - the traceability matrix, the phased plan, the research appendix, the implementation report and the knowledge base. Same content as markdown under `markdown\`, which is also what the ERP-MSCAST project on claude.ai holds. |
| **erpnext-poc** | Everything that builds and runs the POC: scripts, seed data, backups. Start with `erpnext-poc\README.md`, and `REBUILD.md` if you ever need to rebuild from nothing. |

## Where the POC lives

It runs in Docker inside WSL, not in this folder. This folder holds the scripts that drive it.

- Local: http://localhost:8080 · Public: https://mscast.carobar.net
- Start it: `wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/start-poc.sh`
- Check it: `wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness`

## Status

All 97 requirements from MSCAST's requirement document are implemented; 23 of 23 automated checks
pass. Six items rest on assumptions that MSCAST or the CA should confirm - they are listed in the
implementation report and written into the voucher narrations inside the system.

Version history of the documents is not kept here. Older versions were removed on 19 Sep 2026;
the claude.ai project holds the current copies too.
