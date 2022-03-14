ARG VERSION="20.04"
FROM ubuntu:${VERSION}

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG PYTHON_VERSION=3.9
ARG SOPS_VERSION=3.6.1

# Set up non-root user
COPY scripts/non-root-user.sh /tmp/
RUN bash /tmp/non-root-user.sh "${USERNAME}" "${USER_UID}" "${USER_GID}"

# Install system tools
RUN apt-get update && \
    apt-get -y install --no-install-recommends sudo git zsh ca-certificates \
    zip unzip curl jq gettext-base gnupg2 wget iputils-ping apt-transport-https \
    software-properties-common

# Install kustomize
RUN curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash \
    && mv kustomize /usr/local/bin/kustomize

# Install flux
RUN curl -s -L https://toolkit.fluxcd.io/install.sh | sudo bash

# Install kubectl
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl
    
# Install sops
RUN wget https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops_${SOPS_VERSION}_amd64.deb  \
    && dpkg -i sops_${SOPS_VERSION}_amd64.deb

# Install helm
RUN curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -\
    && echo "deb https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list \
    && apt-get update \
    && apt-get install helm

# Install python
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get -y install python${PYTHON_VERSION} libpython${PYTHON_VERSION}-dev python3-pip python${PYTHON_VERSION}-venv gcc \
       build-essential libssl-dev libffi-dev python-dev libxml2-dev libxslt1-dev \
       libblas-dev libatlas-base-dev zlib1g-dev \
    && update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

