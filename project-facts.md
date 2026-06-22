# Project Facts: learn-hub

> Auto-generiert von `platform/.github/scripts/push_project_facts.py`
> Letzte Aktualisierung: 2026-06-22 — bei Änderungen: `platform/gen-project-facts.yml` triggern

## Meta

- **Type**: `django`
- **GitHub**: `https://github.com/achimdehnert/learn-hub`
- **Branch**: `main` — push: `git push` (SSH-Key konfiguriert)

## Lokale Umgebung (Dev Desktop — adehnert)

- **Pfad**: `~/CascadeProjects/learn-hub` → `$GITHUB_DIR` = `~/CascadeProjects`
- **src_root**: `./` (root) — `manage.py` liegt dort
- **pythonpath**: `./`
- **Venv**: `~/CascadeProjects/learn-hub/.venv/bin/python`
- **MCP aktiv**: `mcp0_` = github · `mcp1_` = orchestrator

## Settings

- **Prod-Modul**: `config.settings.production`
- **Test-Modul**: `config.settings.test`
- **Testpfad**: `tests/`

## Stack

- **Django**: `5.x`
- **Python**: `3.12`
- **PostgreSQL**: `16`
- **HTMX installiert**: nein
- **HTMX-Detection**: `request.headers.get("HX-Request") == "true"`


## Apps

- `core`
- `learnfw_migrations`
- `learning`

## Infrastruktur

- **Prod-URL**: `learn.iil.pet`
- **Staging-URL**: `staging.learn.iil.pet`
- **Port**: `8100`
- **Health-Endpoint**: `/livez/`
- **DB-Name**: `learn_hub`

## System (Hetzner Server)

- devuser hat **KEIN sudo-Passwort** → System-Pakete immer via SSH als root:
  ```bash
  ssh root@localhost "apt-get install -y <package>"
  ```
