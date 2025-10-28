# Bewertungsapp

## Quickstart with docker

### 1. Clone the repository

### 2. Create environment files

<pre lang="md"><code>cp .env.example .env</code></pre>

### 3. Build and start the containers with docker compose

`docker compose up --build -d`

### After startup

- Frontend : http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

## Datenbankmigration

### 1. Pull the newest changes

### 2. Rebuild the docker containers

`docker compose up --build -d`

### 3. Apply the newest migration version with alembic

`docker-compose exec backend alembic upgrade head`




