### Practice App

Practice

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app practice_app
```

### Hosting on Render (Docker)

This repository includes a production-ready `Dockerfile`, `render.yaml`, and `entrypoint.sh` for deploying to [Render](https://render.com):

1. **Option A: 1-Click Blueprint**:
   - In Render Dashboard, click **New +** → **Blueprint**.
   - Connect this repository. Render will automatically detect `render.yaml` and configure the Web Service and Persistent Disk.

2. **Option B: Manual Web Service**:
   - In Render Dashboard, click **New +** → **Web Service**.
   - Connect this repository (`https://github.com/dharsha2005/practice-app`).
   - Select **Docker** as the environment.
   - Recommended Plan: **Standard (2 GB RAM)** (Frappe requires at least 1 GB RAM).
   - Set environment variables as needed:
     - `PORT`: `10000` (Render handles this dynamically)
     - `SITE_NAME`: `practice.localhost` (or your domain)
     - `ADMIN_PASSWORD`: `<your-secure-password>`
     - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (if connecting to external MariaDB/PostgreSQL)
     - `REDIS_CACHE_URL`, `REDIS_QUEUE_URL` (if connecting to managed Redis)
   - Add a **Persistent Disk** mounted at `/home/frappe/frappe-bench/sites` so site data persists across deploys.


### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/practice_app
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
