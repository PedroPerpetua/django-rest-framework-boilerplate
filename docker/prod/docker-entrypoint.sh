#!/bin/sh
set -e

# Parse the log level
LOG_LEVEL_INT=${LOG_LEVEL:0}

case "$LOG_LEVEL_INT" in
  10) LOG_LEVEL_STR="debug" ;;
  20) LOG_LEVEL_STR="info" ;;
  30) LOG_LEVEL_STR="warn" ;;
  40) LOG_LEVEL_STR="error" ;;
  *) LOG_LEVEL_STR="crit" ;;
esac

# Parse the cors config from env
# TODO: is this the best way?
CORS_STR=""
OLD_IFS=$IFS
IFS=','
for ORIGIN in $CORS_ALLOWED_ORIGINS; do
    ORIGIN=$(echo "$ORIGIN" | xargs)
    CORS_STR="${CORS_STR}        ~^${ORIGIN}$ \$http_origin;\n"
done
IFS=$OLD_IFS

# Replace both values
sed \
    -e "s\`__CORS_ALLOWED_ORIGINS__\`$CORS_STR\`" \
    -e "s|__LOG_LEVEL__|$LOG_LEVEL_STR|" \
    /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Setup Django
python manage.py setup

# Start supervisord
exec supervisord -c /etc/supervisor.d/supervisord.ini
