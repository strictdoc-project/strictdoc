#!/bin/sh

# This custom entrypoint script is needed for creating a container user with
# a host's UID/GUI which enables sharing of the files between the container
# and the host.

set -e

# Ensure we have the environment variables
if [ -z "$HOST_UID" ] || [ -z "$HOST_GID" ]; then
    echo "HOST_UID and HOST_GID must be set!"
    exit 1
fi

echo "strictdoc/docker: running a Docker container entrypoint."
echo "strictdoc/docker: ensuring strictdoc user with UID=$HOST_UID and GID=$HOST_GID exists"

# Check if a user with this UID already exists (e.g., "ubuntu")
EXISTING_USER=$(getent passwd "$HOST_UID" | cut -d: -f1)

if [ -n "$EXISTING_USER" ]; then
    echo "error: strictdoc/docker: detected a wrong user: '$EXISTING_USER'. Ensure that any default users are removed from the Dockerfile. This entrypoint script is supposed to create a new user 'strictdoc'."
    exit 1
else
    # Ensure the group exists.
    EXISTING_GROUP=$(getent group "$HOST_GID" | cut -d: -f1)
    if [ -z "$EXISTING_GROUP" ]; then
        echo "strictdoc/docker: creating new group strictdoc with GID=$HOST_GID"
        groupadd -g "$HOST_GID" strictdoc
    else
        echo "strictdoc/docker: group with GID=$HOST_GID already exists: $EXISTING_GROUP, reusing it."
    fi

    # Create the user.
    echo "strictdoc/docker: creating new user strictdoc with UID=$HOST_UID"
    useradd -m -u "$HOST_UID" -g "$HOST_GID" -s /bin/bash strictdoc

    # Give the user root privileges. Useful for debugging.
    echo "strictdoc ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/strictdoc
fi

echo "strictdoc/docker: show created user info:"
id strictdoc

# Run as the correct user. If no command is provided, run a shell.
if [ $# -eq 0 ]; then
    echo "strictdoc/docker: no command provided, opening an interactive shell."
    exec gosu strictdoc /bin/bash
else
    # Otherwise, run the provided command.
    exec gosu strictdoc "$@"
fi
