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
    gosu \
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

# Create a virtual environment in the user's home directory.
RUN python3 -m venv /opt/venv

# Ensure the virtual environment is used by modifying the PATH.
ENV PATH="/opt/venv/bin:$PATH"

# This checkout (`Robotics010/strictdoc`) is itself a fork with course-specific
# code under strictdoc/ (e.g. features/eurobot_test_dashboard,
# features/project_statistics) that has never been published to PyPI or merged
# upstream, so "local" is the only source that actually matches what's in this
# repo. "pypi"/a git ref are kept for anyone building this Dockerfile against a
# vanilla StrictDoc checkout instead.
COPY . /strictdoc-src

ARG STRICTDOC_SOURCE="local"
ENV STRICTDOC_SOURCE=${STRICTDOC_SOURCE}

RUN pip install --no-cache-dir --upgrade pip; \
    if [ "$STRICTDOC_SOURCE" = "pypi" ]; then \
      pip install --no-cache-dir strictdoc; \
    elif [ "$STRICTDOC_SOURCE" = "local" ]; then \
      pip install --no-cache-dir /strictdoc-src; \
    else \
      pip install --no-cache-dir git+https://github.com/Robotics010/strictdoc.git@${STRICTDOC_SOURCE}; \
    fi; \
    chmod -R 777 /opt/venv;

# Remove the default 'ubuntu' user.
RUN userdel -r ubuntu 2>/dev/null || true

# Allow updating the UID/GID dynamically at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the working directory to the user's home directory.
WORKDIR /data

ENTRYPOINT ["/entrypoint.sh"]
