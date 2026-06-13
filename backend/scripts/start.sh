#!/bin/sh
set -e

echo "Waiting for database..."
attempt=1
max_attempts=30
until alembic upgrade head; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Database migration failed after ${max_attempts} attempts"
    exit 1
  fi
  echo "Migration attempt ${attempt} failed — retrying in 3s..."
  attempt=$((attempt + 1))
  sleep 3
done

if [ "${SEED_ON_STARTUP:-true}" = "true" ]; then
  python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
