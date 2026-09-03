# ---- Stage 1: build React ----
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Django ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/

# Copy the built React app
COPY --from=frontend-build /frontend/dist /app/static/frontend
RUN mkdir -p /app/templates/frontend \
    && cp /app/static/frontend/index.html /app/templates/frontend/index.html

RUN mkdir -p /app/media /app/staticfiles \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]