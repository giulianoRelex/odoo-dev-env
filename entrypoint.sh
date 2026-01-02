#!/bin/bash
set -e

# Wait for the database using the implicit wait or custom check if needed.
# Since depends_on + service_healthy is used, we assume DB is up.

if [ "$DEBUGPY" = "True" ]; then
    echo "Installing debugpy..."
    pip install debugpy -t /tmp/debugpy --no-cache-dir
    CMD="python3"
    ARGS=("-m" "debugpy" "--listen" "0.0.0.0:5678" "/usr/bin/odoo" "--config=/etc/odoo/odoo.conf" "--db-filter=${DB_FILTER}")
else
    CMD="odoo"
    ARGS=("--config=/etc/odoo/odoo.conf" "--db-filter=${DB_FILTER}")
fi

# Helper function to check if language exists
check_language_exists() {
    python3 -c "
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        host=os.environ.get('HOST', 'db'),
        user=os.environ.get('USER', 'odoo'),
        password=os.environ.get('PASSWORD', 'odoo'),
        dbname=os.environ.get('POSTGRES_DB', 'odoo_db')
    )
    cur = conn.cursor()
    cur.execute(\"SELECT 1 FROM res_lang WHERE code = %s\", (os.environ.get('LOAD_LANGUAGE'),))
    exists = cur.fetchone()
    if exists:
        sys.exit(0) # Exists
    else:
        sys.exit(1) # Not exists
except Exception as e:
    # If connection fails or DB doesn't exist yet (first run), we assume it doesn't exist
    # But wait, if DB doesn't exist, psycopg2 will fail to connect to 'odoo_db'.
    # In that case, Odoo will create it. So language definitely doesn't exist.
    sys.exit(1) 
"
}

# Add WITHOUT_DEMO if set
if [ -n "$WITHOUT_DEMO" ]; then
    ARGS+=("--without-demo=${WITHOUT_DEMO}")
fi

# Init modules handling
MODULES_TO_INIT="${INIT_MODULES}"

# Language Loading Logic
if [ -n "$LOAD_LANGUAGE" ]; then
    echo "Checking if language $LOAD_LANGUAGE is already loaded..."
    if check_language_exists; then
        echo "Language $LOAD_LANGUAGE already exists. Skipping load."
    else
        echo "Language $LOAD_LANGUAGE not found or DB not initialized. Adding --load-language flag and forcing base init."
        ARGS+=("--load-language=${LOAD_LANGUAGE}")
        # Force 'base' initialization to ensure DB tables are created
        if [[ -z "$MODULES_TO_INIT" ]]; then
            MODULES_TO_INIT="base"
        else
            MODULES_TO_INIT="$MODULES_TO_INIT,base"
        fi
    fi
fi

# Apply init modules if any
if [ -n "$MODULES_TO_INIT" ]; then
    ARGS+=("--init=${MODULES_TO_INIT}")
fi

# Always add dev mode for hot reloading in this dev environment
ARGS+=("--dev=reload,xml")

echo "Starting Odoo with command: $CMD ${ARGS[*]}"
exec $CMD "${ARGS[@]}"
