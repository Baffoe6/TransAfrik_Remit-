# Deployment Guide — TransAfrik Remit MVP

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://app.ipaygo.co.za |
| API | https://api.ipaygo.co.za |
| Health | https://api.ipaygo.co.za/health |

## Railway (Backend)

### Required variables

```
ENVIRONMENT=production
SECRET_KEY=<openssl rand -hex 32>
DATABASE_URL=<from Postgres plugin>
REDIS_URL=<from Redis plugin>
CORS_ORIGINS=https://app.ipaygo.co.za
ENABLE_DEV_ENDPOINTS=false
DOCS_ENABLED=false
SEED_DEMO_DATA=false
SEED_ON_STARTUP=true
REQUIRE_HTTPS=true
```

### Deploy steps

1. Link PostgreSQL + Redis plugins
2. Set root directory to `backend`
3. Deploy from `main` branch
4. Run migrations on startup (Dockerfile `scripts/start.sh`)

## Vercel (Frontend)

```
NEXT_PUBLIC_API_URL=https://api.ipaygo.co.za
```

Custom domain: `app.ipaygo.co.za`

## Post-deploy checklist

1. `GET /health` returns `7.0.0-mvp`
2. `GET /admin/launch-readiness` ≥ 80%
3. Login as `admin@transafrik.co.za`
4. Test waitlist at `/waitlist`
5. Verify CORS from `app.ipaygo.co.za`

## Migrations

```bash
cd backend
alembic upgrade head
python -m app.seed   # production: SEED_DEMO_DATA=false
```

## Rollback

```bash
alembic downgrade 008
```
