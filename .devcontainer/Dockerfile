FROM python:3.10-slim-bookworm

# Prevent interactive prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# - git: Required for DevPod/VSCode source control
# - libgl1-mesa-glx & libglib2.0-0: Required by OpenCV
# - doxygen & graphviz: Required for generating documentation
RUN apt-get update && apt-get -y install --no-install-recommends \
    git \
    sudo \
    libgl1-mesa-glx \
    libglib2.0-0 \
    doxygen \
    graphviz \
    nano \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ccache \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Standard best practice for Devcontainers)
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to the non-root user
USER $USERNAME
WORKDIR /workspace

# Ensure local user binaries (like pytest) are on the PATH
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Install core Python testing and formatting tools
RUN pip install --user --no-cache-dir pytest pytest-cov black flake8
