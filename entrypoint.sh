#!/bin/bash
set -e

export PORT="${PORT:-8000}"
export SITE_NAME="${SITE_NAME:-practice.localhost}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
export ENABLE_WORKERS="${ENABLE_WORKERS:-true}"
export FRAPPE_BENCH_DIR="/home/frappe/frappe-bench"

cd "${FRAPPE_BENCH_DIR}"

mkdir -p logs sites/assets

# Start internal Redis if no external Redis is provided
if [ -z "$REDIS_CACHE" ] && [ -z "$REDIS_HOST" ] && [ -z "$REDIS_CACHE_URL" ]; then
    echo "Starting local Redis daemon..."
    redis-server --daemonize yes
fi

# Ensure sites directory permissions if mounted as volume
chown -R frappe:frappe sites logs || true

# Configure default site routing for Render domain mapping
python3 - <<EOF
import json, os

sites_path = "sites"
conf_path = os.path.join(sites_path, "common_site_config.json")
data = {}
if os.path.exists(conf_path):
    try:
        with open(conf_path, "r") as f:
            data = json.load(f)
    except Exception:
        pass

data["serve_default_site"] = True
data["default_site"] = os.environ.get("SITE_NAME", "practice.localhost")
data["dns_multitenant"] = False

if os.environ.get("REDIS_CACHE_URL"):
    data["redis_cache"] = os.environ.get("REDIS_CACHE_URL")
if os.environ.get("REDIS_QUEUE_URL"):
    data["redis_queue"] = os.environ.get("REDIS_QUEUE_URL")

with open(conf_path, "w") as f:
    json.dump(data, f, indent=2)

with open(os.path.join(sites_path, "currentsite.txt"), "w") as f:
    f.write(os.environ.get("SITE_NAME", "practice.localhost") + "\n")
EOF

# Database initialization / migration if DB_HOST is set
if [ -n "$DB_HOST" ]; then
    echo "External database host detected: $DB_HOST"
    DB_TYPE="${DB_TYPE:-mariadb}"
    DB_PORT="${DB_PORT:-3306}"
    [ "$DB_TYPE" = "postgres" ] && DB_PORT="${DB_PORT:-5432}"

    if [ ! -d "sites/${SITE_NAME}" ]; then
        echo "Creating new site ${SITE_NAME}..."
        su frappe -c "bench new-site ${SITE_NAME} \
            --db-type ${DB_TYPE} \
            --db-host ${DB_HOST} \
            --db-port ${DB_PORT} \
            --db-name ${DB_NAME:-frappe} \
            --db-password ${DB_PASSWORD} \
            --admin-password ${ADMIN_PASSWORD} \
            --install-app practice_app \
            --force" || true
    else
        echo "Site ${SITE_NAME} exists. Running migrations..."
        su frappe -c "bench --site ${SITE_NAME} migrate" || true
    fi
else
    # Fallback to local MariaDB if no external database was provided
    if command -v mariadbd >/dev/null 2>&1 || command -v mysqld >/dev/null 2>&1; then
        echo "Starting local MariaDB service..."
        service mariadb start || true
        if [ ! -d "sites/${SITE_NAME}" ]; then
            echo "Initializing local site ${SITE_NAME}..."
            su frappe -c "bench new-site ${SITE_NAME} \
                --admin-password ${ADMIN_PASSWORD} \
                --install-app practice_app \
                --force" || true
        else
            echo "Running local migrations..."
            su frappe -c "bench --site ${SITE_NAME} migrate" || true
        fi
    else
        echo "Notice: DB_HOST is not set. Site creation requires database credentials."
    fi
fi

# Pass control to supervisor or user command
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    echo "Starting Supervisord on port ${PORT}..."
    exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/frappe.conf
fi
