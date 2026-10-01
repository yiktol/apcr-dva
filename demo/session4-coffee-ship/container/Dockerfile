# coffee-shop container image: multi-stage build.
#
# Build context is this directory (`container/`) — both `deploy.sh` and
# `buildspec.yml` run `docker build container/`, so everything the build needs
# lives inside the context: the SPA source at `container/frontend/` and the
# architecture diagram at `container/architecture.svg`.
#
# Stage 1 (node:20-alpine) builds the Vite SPA to `/build/dist`.
# Stage 2 (python:3.12-slim) is the runtime: a boto3 Python HTTP server that
# serves the baked SPA from /app/static plus the JSON API (DynamoDB + SSM).

# --- Stage 1: build the SPA ---
FROM node:20-alpine AS build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: python runtime ---
FROM python:3.12-slim
WORKDIR /app

# Install the Python runtime dependencies (boto3) before copying app code so
# the pip layer is cached independently of app.py changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./

# Bake the built SPA and the architecture diagram into the static root.
COPY --from=build /build/dist /app/static
COPY architecture.svg /app/static/architecture.svg

# Container port; matches the ECS taskdef portMapping and the ALB target.
ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
