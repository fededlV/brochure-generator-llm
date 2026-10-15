# SSL / TLS Certificates Directory

This directory is reserved for mounting SSL/TLS certificates when enabling HTTPS on the NGINX reverse proxy.

## Setting Up Custom or Let's Encrypt Certificates:

1. Place your certificates here:
   - Certificate chain: `fullchain.pem`
   - Private key: `privkey.pem`

2. Set proper file permissions (read-only for NGINX unprivileged user):
   ```bash
   chmod 600 nginx/certs/privkey.pem
   chmod 644 nginx/certs/fullchain.pem
   ```

3. Uncomment the SSL server block in `nginx/conf.d/default.conf`.

4. In `docker-compose.yml`, mount this directory to the proxy service:
   ```yaml
   volumes:
     - ./nginx/certs:/etc/nginx/certs:ro
   ```

5. Restart the containers:
   ```bash
   docker compose restart nginx
   ```
