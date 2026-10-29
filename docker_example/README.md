# Run Primeagent with Docker

This guide will help you get Primeagent up and running using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Steps

1. Clone the Primeagent repository:

   ```sh
   git clone https://github.com/khulnasoft-bot/primeagent.git
   ```

2. Navigate to the `docker_example` directory:

   ```sh
   cd primeagent/docker_example
   ```

3. Create a `.env` file with the Primeagent admin password set:

   ```sh
   PRIMEAGENT_SUPERUSER_PASSWORD=SUPERUSER_PASSWORD
   ```

   Replace `SUPERUSER_PASSWORD` with a strong password for the Primeagent superuser.
   The default admin username is `primeagent`.

4. Run the Docker Compose file:

   ```sh
   docker compose up
   ```

Primeagent will now be accessible at [http://localhost:7860/](http://localhost:7860/).

## Configure Docker Compose

The Docker Compose configuration spins up two services: `primeagent` and `postgres`.

### Primeagent service

The `primeagent` service uses the `khulnasoft/primeagent:latest` Docker image and exposes port 7860. It depends on the `postgres` service.

Environment variables:

- `PRIMEAGENT_DATABASE_URL`: The connection string for the PostgreSQL database.
- `PRIMEAGENT_SUPERUSER_PASSWORD`: The initial admin password. This value is required in `.env`.
- `PRIMEAGENT_CONFIG_DIR`: The directory where Primeagent stores logs, file storage, monitor data, and secret keys.

Volumes:

- `primeagent-data`: This volume is mapped to `/app/primeagent` in the container.

### PostgreSQL service

The `postgres` service uses the `postgres:16-trixie` Docker image and exposes port 5432. The image is pinned to a specific Debian base (`trixie`, Debian 13) so the `postgres:16` tag cannot silently roll its underlying OS, which would otherwise produce a glibc collation version mismatch warning on existing data volumes.

Environment variables:

- `POSTGRES_USER`: The username for the PostgreSQL database.
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database.
- `POSTGRES_DB`: The name of the PostgreSQL database.

Volumes:

- `primeagent-postgres`: This volume is mapped to `/var/lib/postgresql/data` in the container.

### Upgrading from a `bookworm`-initialized volume

Earlier versions of this example used `postgres:16`, which initially shipped on Debian Bookworm (glibc 2.36). The pinned image now uses Trixie (glibc 2.41). On the first start against a volume that was initialized under Bookworm, PostgreSQL logs a one-time warning:

```
WARNING: database "primeagent" has a collation version mismatch
DETAIL: The database was created using collation version 2.36, but the operating system provides version 2.41.
```

To clear it, refresh the collation version against the running database (one-off, takes seconds on a typical Primeagent database):

```sh
docker compose exec postgres \
  psql -U primeagent -d primeagent \
  -c "REINDEX DATABASE primeagent;" \
  -c "ALTER DATABASE primeagent REFRESH COLLATION VERSION;"
```

Fresh installs are unaffected.

## Switching to a specific Primeagent version

If you want to use a specific version of Primeagent, you can modify the `image` field under the `primeagent` service in the Docker Compose file. For example, to use version 1.0-alpha, change `khulnasoft/primeagent:latest` to `khulnasoft/primeagent:1.0-alpha`.
