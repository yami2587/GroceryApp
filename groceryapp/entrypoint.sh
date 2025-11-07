#!/bin/bash
set -e

# wait for Postgres (simple)
if [ -n "$DATABASE_HOST" ]; then
  echo "Waiting for postgres..."
  while ! pg_isready -h $DATABASE_HOST -p ${DATABASE_PORT:-5432} -U "$DATABASE_USER" >/dev/null 2>&1; do
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput


if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
    u='$DJANGO_SUPERUSER_USERNAME'; e='$DJANGO_SUPERUSER_EMAIL'; p='$DJANGO_SUPERUSER_PASSWORD'; \
    User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p)"
fi

exec "$@"
