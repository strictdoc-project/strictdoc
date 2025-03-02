# Usage:
#
# /strictdoc$ docker build . -t strictdoc:latest
# /strictdoc$ docker run --name strictdoc --rm -v "$(pwd):/data" -i -t strictdoc:latest
# bash-5.1# strictdoc export .
# bash-5.1# exit
# strictdoc$ firefox docs/output/html/index.html

FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    sudo \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome
RUN wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome.deb \
    && rm google-chrome.deb

# Create a new non-root user and group.
# NOTE: It is important that a non-root user is used because otherwise the
# Chrome Driver fails with: "User data directory is already in use"
# https://github.com/SeleniumHQ/selenium/issues/15327#issuecomment-2688613182
RUN groupadd -r strictdoc_user && useradd -r -m -g strictdoc_user strictdoc_user

# Grant the new user sudo privileges.
RUN echo "strictdoc_user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/strictdoc_user

# Create a virtual environment in the user's home directory.
RUN python3 -m venv /opt/venv

# Ensure the virtual environment is used by modifying the PATH.
ENV PATH="/opt/venv/bin:$PATH"

# Install StrictDoc. Set default StrictDoc installation from PyPI but allow
# overriding it with an environment variable.
ARG STRICTDOC_SOURCE="pypi"
ENV STRICTDOC_SOURCE=${STRICTDOC_SOURCE}

RUN if [ "$STRICTDOC_SOURCE" = "pypi" ]; then \
      pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir strictdoc; \
    else \
      pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir git+https://github.com/strictdoc-project/strictdoc.git@${STRICTDOC_SOURCE}; \
    fi; \
    chmod -R 777 /opt/venv;

USER strictdoc_user

# Set the working directory to the user's home directory.
WORKDIR /data

ENTRYPOINT ["/bin/bash"]
