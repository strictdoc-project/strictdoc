# Usage:
#
# /strictdoc$ docker build \
#                 ./ \
#                 --build-arg STRICTDOC_SOURCE=pypi \
#                 --tag strictdoc:latest
# /strictdoc$ docker run \
#                 --rm \
#                 --volume="$(pwd):/data/" \
#                 --user=$(id -u):$(id -g) \
#                 --userns=host \
#                 --network=host \
#                 --hostname="strictdoc" \
#                 --name="strictdoc" \
#                 --init \
#                 --tty \
#                 strictdoc:latest \
#                     export ./
# /strictdoc$ firefox ./output/html/index.html

FROM ubuntu:24.04

# Workaround: Newly introduced `ubuntu` user in ubuntu:24.04 causes UID/GID
# mapping issues when adding custom user.
RUN touch /var/mail/ubuntu && \
    chown ubuntu /var/mail/ubuntu && \
    userdel --remove ubuntu

# Main "payload" software
ARG PAYLOAD=strictdoc

# Docker image labels
LABEL maintainer="StrictDoc Project"
LABEL name="${PAYLOAD}"
LABEL description="Software for technical documentation and requirements management."

# Install dependencies
RUN apt-get update && apt-get install --assume-yes --no-install-recommends \
        curl \
        git \
        python3 \
        python3-pip \
        python3-venv \
        vim \
        wget \
    && \
    rm --recursive --force /var/lib/apt/lists/*

# Download and install Google Chrome
RUN wget --quiet --output-document=google-chrome.deb \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install --assume-yes --no-install-recommends ./google-chrome.deb && \
    rm --recursive --force /var/lib/apt/lists/* && \
    rm --force google-chrome.deb

# Create a virtual environment and ensure it is used by modifying the PATH.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

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
    fi;

# Switch to non-root user
RUN groupadd ${PAYLOAD} && \
    useradd --no-log-init --gid ${PAYLOAD} ${PAYLOAD}
USER ${PAYLOAD}

# Set up working directory.
WORKDIR /data/

# Execute StrictDoc by default
ENTRYPOINT ["strictdoc"]
CMD ["--help"]
