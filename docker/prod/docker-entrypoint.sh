#!/bin/sh
set -e

# Take the cors config from the env and set it on the template
# TODO: is this the best way?
REPLACEMENT=""
OLD_IFS=$IFS
IFS=','
for ORIGIN in $CORS_ALLOWED_ORIGINS; do
    ORIGIN=$(echo "$ORIGIN" | xargs)
    REPLACEMENT="${REPLACEMENT}        ~^${ORIGIN}$ \$http_origin;\n"
done
IFS=$OLD_IFS
sed "s\`__CORS_ALLOWED_ORIGINS__\`$REPLACEMENT\`" /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Setup Django
python manage.py setup

# Start supervisord
exec supervisord -c /etc/supervisor.d/supervisord.ini
