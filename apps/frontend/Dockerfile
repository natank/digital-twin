# Digital Twin frontend (React + Vite)
# Build from monorepo root:
#   docker build -f apps/frontend/Dockerfile -t digital-twin-frontend .

FROM node:20-alpine AS builder

WORKDIR /app

RUN corepack enable

# Workspace manifests first for dependency layer caching.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml nx.json tsconfig.base.json tsconfig.json ./
COPY apps/frontend/package.json ./apps/frontend/package.json
COPY libs/frontend-shared/package.json ./libs/frontend-shared/package.json

RUN pnpm install --frozen-lockfile

# Application sources required for the Vite/Nx build.
COPY apps/frontend ./apps/frontend
COPY libs/frontend-shared ./libs/frontend-shared
COPY vitest.workspace.ts ./vitest.workspace.ts

# Production build (output: apps/frontend/dist)
ENV NODE_ENV=production
RUN pnpm nx build frontend

# ---------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

COPY apps/frontend/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
