# ==============================================================================
# NGINX Reverse Proxy Dockerfile
# Non-root unprivileged execution with hardened security configuration
# ==============================================================================

FROM nginxinc/nginx-unprivileged:alpine

# Copy custom unprivileged main configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy virtual host configuration with security headers & proxy routing
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# Expose unprivileged HTTP (8080) and HTTPS (8443) ports
EXPOSE 8080 8443

# Built-in container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:8080/healthz || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
