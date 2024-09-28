# syntax=docker/dockerfile:1.9
FROM ubuntu:noble AS build

# The following does not work in Podman unless you build in Docker
# compatibility mode: <https://github.com/containers/podman/issues/8477>
# You can manually prepend every RUN script with `set -ex` too.
SHELL ["sh", "-exc"]

### Start Build Prep.
### This should be a separate build container for better reuse.

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    rsync \
    ca-certificates \
    curl \
    python3-setuptools \
    python3.12-dev
EOT

# Security-conscious organizations should package/review uv themselves.
COPY --from=ghcr.io/astral-sh/uv:0.4.13 /uv /bin/uv

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/app` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app

### End Build Prep -- this is where your Dockerfile should start.

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

# Prepare a virtual environment.
# This is cached until the Python version changes above.
#
# Note: This will not succeed if you are referencing nomnom's development version
# unless you re-build the uv lock without sources and with prereleases.
RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync \
    --frozen \
    --no-dev \
    --no-sources \
    --no-install-project
EOT

# Now install the APPLICATION from `/src` without any dependencies.
# `/src` will NOT be copied into the runtime container.
# LEAVE THIS OUT if your application is NOT a proper Python package.
# We can’t use `uv sync` here because that only does editable installs:
# <https://github.com/astral-sh/uv/issues/5792>
COPY . /src
RUN --mount=type=cache,target=/root/.cache \
    uv pip install \
        --python=$UV_PROJECT_ENVIRONMENT \
        --no-deps \
        /src

# Copy in the Django stuff, too:
RUN <<EOT
rsync -av /src/manage.py /src/.env.dockertest /src/ /src/glasgow_2024_app /app/
EOT

# Copy in the docker scripts
RUN <<EOT
install -v -d -m 0755 /app/docker
install -v -m 0755 /src/docker/start.sh /app/docker/
install -v -m 0755 /src/docker/entrypoint.sh /app/docker/entrypoint.sh
EOT

##########################################################################

FROM ubuntu:noble AS run
SHELL ["sh", "-exc"]

# add the application virtualenv to search path.
ENV PATH=/app/bin:$PATH

# Don't run your app as root.
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

ENTRYPOINT ["/usr/bin/tini", "-v", "--", "/app/docker/entrypoint.sh"]
# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

# Note how the runtime dependencies differ from build-time ones.
# Notably, there is no uv either!
RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    python3.12 \
    libpython3.12 \
    libpcre3 \
    libxml2 \
    tini \
    dotenv

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Copy the pre-built `/app` directory to the runtime container
# and change the ownership to user app and group app in one step.
COPY --from=build --chown=app:app /app /app

# If your application is NOT a proper Python package that got
# pip-installed above, you need to copy your application into
# the container HERE:
# COPY . /app/whereever-your-entrypoint-finds-it

# prepare the working paths
RUN <<EOT
install -v -d -m 0755 -o app -g app /staticfiles
EOT

VOLUME /staticfiles

USER app
WORKDIR /app

EXPOSE 8000

# Strictly optional, but I like it for introspection of what I've built.
RUN <<EOT
python -V
python -Im site
find /app -not \( -path '*/.venv/*' -o -path '/app/lib/*' \)
# set so that manage.py will be working
dotenv-rust --file .env.dockertest python manage.py check
rm .env.dockertest
EOT

# To develop _in_ this dockerfile:
# build this image: docker build --target dev -t glasgow-2024:dev .
# run it: docker run --rm -it --env-file .env --env-file .env.docker --network glasgow-2024_default --name nomnom-dev glasgow-2024:dev
FROM run AS dev

USER root

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    postgresql-client \
    redis
EOT

USER app

CMD ["/app/docker/start.sh", "server"]
# The real, deployable image is `run` above, but we want it to also be the default.
FROM run
