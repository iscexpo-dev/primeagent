# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# BUILDER
# Used to build WFX and create our virtual environment
################################

# Use an Alpine-based Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:latest AS uv_installer
FROM registry.access.redhat.com/ubi10/python-314-minimal AS builder
USER root
COPY --from=uv_installer /uv /usr/local/bin/uv
COPY --from=uv_installer /uvx /usr/local/bin/uvx

# Install build dependencies needed for some Python packages on Alpine
RUN microdnf install -y python3.14-devel tar xz gcc gcc-c++ make libaio-devel kernel-headers

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# --- Copy only files that affect dependency resolution (best cache) ---
# Workspace root metadata + lockfile
COPY pyproject.toml uv.lock ./

# Member pyproject files so uv knows about workspace packages (no source yet, better cache)
COPY src/wfx/pyproject.toml /app/src/wfx/pyproject.toml
COPY src/wfx/README.md /app/src/wfx/README.md
COPY src/sdk/pyproject.toml /app/src/sdk/pyproject.toml
COPY src/sdk/README.md /app/src/sdk/README.md

# Create the venv and install *only* what wfx needs (no dev)
# We expect some packages to be built from source, so we mount the cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package wfx

# --- Now copy the source (doesn't bust the deps layer) ---
COPY src/wfx/src /app/src/wfx/src
COPY src/sdk/src /app/src/sdk/src

# Install the WFX package into the virtual environment (non-editable)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package wfx

################################
# RUNTIME
# Setup user, utilities and copy the virtual environment only
################################
FROM registry.access.redhat.com/ubi10/python-314-minimal AS runtime
USER root
# Create a non-root user
# -D: Don't assign a password
# -u: Set user ID
# -G: Add to group (root)
# -h: Set home directory
# -s: Set shell
RUN microdnf install -y tar xz shadow-utils && useradd -u 1000 -g 0 --no-create-home -d /app/data -s /sbin/nologin wfx

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=1000 /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV HOME=/app/data
ENV PRIMEAGENT_AUTO_LOGIN=false
ENV BASH_ENV="" \
    ENV="" \
    PROMPT_COMMAND=""

RUN mkdir -p /app/data \
    && chown -R 1000:0 /app/data \
    && chmod -R g+rwX /app/data

LABEL org.opencontainers.image.title=wfx
LABEL org.opencontainers.image.authors=['Primeagent']
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.url=https://github.com/khulnasoft-bot/primeagent
LABEL org.opencontainers.image.source=https://github.com/khulnasoft-bot/primeagent
LABEL org.opencontainers.image.description="WFX - Primeagent Executor CLI Tool"

USER wfx
WORKDIR /app/data

# Default command shows WFX help
CMD ["wfx", "--help"]
