#!/bin/bash
set -e

export PORT="${PORT:-8000}"
export SITE_NAME="${RENDER_EXTERNAL_HOSTNAME:-${SITE_NAME:-practice.localhost}}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
export ENABLE_WORKERS="${ENABLE_WORKERS:-true}"
export FRAPPE_BENCH_DIR="/home/frappe/frappe-bench"

cd "${FRAPPE_BENCH_DIR}"

mkdir -p logs sites/assets /var/run/mysqld
chmod 777 /var/run/mysqld || true

# Start internal Redis if no external Redis is provided
if [ -z "$REDIS_CACHE" ] && [ -z "$REDIS_HOST" ] && [ -z "$REDIS_CACHE_URL" ]; then
    echo "Starting local Redis daemon on port 6379..."
    redis-server --daemonize yes
fi

# Ensure sites directory permissions
chown -R frappe:frappe sites logs || true

# Clean up apps.txt if needed
python3 -c "
p = 'sites/apps.txt'
try:
    apps = [l.strip() for l in open(p) if l.strip()]
    cleaned = []
    for a in apps:
        if a == 'frappepractice_app':
            cleaned.extend(['frappe', 'practice_app'])
        else:
            cleaned.append(a)
    if 'frappe' not in cleaned:
        cleaned.insert(0, 'frappe')
    if 'practice_app' not in cleaned:
        cleaned.append('practice_app')
    dedup = list(dict.fromkeys(cleaned))
    open(p, 'w').write('\n'.join(dedup) + '\n')
except Exception as e:
    print('apps.txt error:', e)
"

# Configure common site config with Redis and default site
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

site_name = os.environ.get("SITE_NAME", "practice.localhost")
data["serve_default_site"] = True
data["default_site"] = site_name
data["dns_multitenant"] = False

# Configure Redis URLs (local fallback to 6379)
data["redis_cache"] = os.environ.get("REDIS_CACHE_URL", os.environ.get("REDIS_CACHE", "redis://127.0.0.1:6379"))
data["redis_queue"] = os.environ.get("REDIS_QUEUE_URL", os.environ.get("REDIS_QUEUE", "redis://127.0.0.1:6379"))
data["redis_socketio"] = os.environ.get("REDIS_SOCKETIO_URL", "redis://127.0.0.1:6379")

with open(conf_path, "w") as f:
    json.dump(data, f, indent=2)

with open(os.path.join(sites_path, "currentsite.txt"), "w") as f:
    f.write(site_name + "\n")
EOF

# Database initialization / migration
if [ -n "$DB_HOST" ]; then
    echo "External database host detected: $DB_HOST"
    DB_TYPE="${DB_TYPE:-mariadb}"
    DB_PORT="${DB_PORT:-3306}"
    [ "$DB_TYPE" = "postgres" ] && DB_PORT="${DB_PORT:-5432}"

    if [ ! -d "sites/${SITE_NAME}" ]; then
        echo "Creating new site ${SITE_NAME} on ${DB_HOST}..."
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
    # Local MariaDB setup
    if command -v mariadbd >/dev/null 2>&1 || command -v mysqld >/dev/null 2>&1; then
        echo "Starting local MariaDB service..."
        service mariadb start || true
        
        # Configure root access for local site creation
        mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('root'); FLUSH PRIVILEGES;" 2>/dev/null || \
        mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" 2>/dev/null || true

        if [ ! -d "sites/${SITE_NAME}" ]; then
            echo "Initializing local site ${SITE_NAME}..."
            su frappe -c "bench new-site ${SITE_NAME} \
                --db-root-username root \
                --db-root-password root \
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

# Enable scheduler and fix assets permissions
su frappe -c "bench --site ${SITE_NAME} enable-scheduler" || true
chmod -R 755 sites/assets || true

# Pass control to supervisor or user command
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    echo "Starting Supervisord on port ${PORT}..."
    exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/frappe.conf
fi
