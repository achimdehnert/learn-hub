# learn-hub

Central Learning Management Hub — [learn.iil.pet](https://learn.iil.pet)

Part of the [IIL Platform](https://github.com/achimdehnert/platform) ecosystem.

## Architecture

- **ADR-140**: Learn-Hub architecture, Shared DB, deployment
- **ADR-139**: `iil-learnfw` package (models, services, API)
- **ADR-137**: Multi-Tenancy (TenantManager, RLS)

### Key Decisions

| # | Decision | Details |
|---|---|---|
| 1 | Authoring-Split (C) | learn-hub for global courses + AI tools |
| 2 | Shared Auth (E) | auth_user + auth_group in learnfw DB |
| 3 | Shared DB (C) | learn-hub = Migrations-Owner, Consumer-Hubs connect via SharedDBRouter |

## Tech Stack

- Python 3.12, Django 5.x
- `iil-learnfw[all]` — Courses, Quizzes, Certificates, Gamification, SCORM
- `iil-aifw` — AI-assisted content generation
- PostgreSQL 16, Redis, Celery
- Docker, GitHub Actions (ADR-120 Reusable Workflows)

## Deployment

| Component | Details |
|---|---|
| Domain | learn.iil.pet |
| Port | 8099 (external) → 8000 (internal) |
| DB Port | 5499 (exposed for Consumer-Hubs) |
| Server | 88.198.191.108 |

## Development

```bash
# Clone
git clone git@github.com:achimdehnert/learn-hub.git
cd learn-hub

# Install
pip install -r requirements/dev.txt

# Run
python manage.py migrate
python manage.py runserver
```

## License

MIT
