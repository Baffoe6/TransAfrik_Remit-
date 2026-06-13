# SSL certificates for staging/production nginx

Place your TLS certificates here before enabling HTTPS:

- `fullchain.pem` — certificate chain
- `privkey.pem` — private key

## Self-signed (staging only)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem -out fullchain.pem \
  -subj "/CN=staging.transafrik.co.za"
```

## Let's Encrypt (production)

Use certbot or your cloud provider's certificate manager, then copy files into this directory.

Nginx listens on port 443 when these files are present. Port 80 continues to serve HTTP for health checks and redirects.
