# ==============================================================================
# Frontend Dockerfile for AI Company Brochure Generator
# Multi-stage build: Node.js 20 builder -> unprivileged Nginx runtime
# ==============================================================================

# Stage 1: Build static assets
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies using package-lock.json for deterministic builds
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline --no-audit

# Copy source and build production bundle
COPY . .
RUN npm run build

# Stage 2: Serve static assets with unprivileged Nginx
FROM nginxinc/nginx-unprivileged:alpine

# Copy custom unprivileged nginx virtual host configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production bundle from build stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose internal unprivileged port (8080)
EXPOSE 8080

# Healthcheck for frontend service
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:8080/healthz || exit 1

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
