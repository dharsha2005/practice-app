FROM python:3.11-slim-bookworm

LABEL maintainer="Dharshan"
LABEL description="Frappe Framework with Practice App for Render deployment"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    python3-dev \
    mariadb-client \
    mariadb-server \
    postgresql-client \
    libmariadb-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    redis-server \
    supervisor \
    cron \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js LTS and Yarn
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

# 3. Create frappe non-root user
RUN useradd -ms /bin/bash frappe

# 4. Install Frappe Bench CLI
USER frappe
WORKDIR /home/frappe
ENV PATH="/home/frappe/.local/bin:${PATH}"
RUN pip install --no-cache-dir --user frappe-bench

# 5. Initialize Frappe Bench (defaults to version-15)
ARG FRAPPE_BRANCH=version-15
RUN bench init --frappe-branch ${FRAPPE_BRANCH} --skip-redis-config-generation --no-procfile --no-backups frappe-bench

# 6. Install Practice App into bench
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/practice_app

RUN ./env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/practice_app \
    && python3 -c "p='sites/apps.txt'; apps=[l.strip() for l in open(p) if l.strip()]; ('practice_app' in apps) or apps.append('practice_app'); open(p,'w').write('\n'.join(apps)+'\n')" \
    && (bench build --app practice_app || true)

# 7. Configure Supervisor & Entrypoint
USER root

RUN ln -sf /home/frappe/.local/bin/bench /usr/local/bin/bench \
    && ln -sf /home/frappe/.local/bin/bench /home/frappe/frappe-bench/env/bin/bench

COPY supervisord.conf /etc/supervisor/conf.d/frappe.conf
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Render default port is dynamic via $PORT (usually 10000)
EXPOSE 8000 10000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
