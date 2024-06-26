#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
#-------------------------------------------------------------------------------------------------------------

FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

ARG NPM_REGISTER="https://registry.npmmirror.com"
ARG PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

#
# Update the OS and maybe install packages
#
ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/http:\/\/deb.debian.org/https:\/\/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# add git lhs to apt
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash

RUN apt-get update \
    && apt-get upgrade -y  \
    && apt-get -y install --no-install-recommends build-essential npm git-lfs fontconfig fonts-noto-cjk dos2unix \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) \
    && wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.5.23/quarto-1.5.23-linux-${arch}.deb \
    && dpkg -i quarto-1.5.23-linux-${arch}.deb \
    && rm -rf /var/lib/apt/lists/* quarto-1.5.23-linux-${arch}.deb \
    && fc-cache -f
ENV DEBIAN_FRONTEND=dialog

# 设置时区为中国上海
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN npm config set registry $NPM_REGISTER && npm install --global yarn
RUN pip config set global.index-url $PIP_INDEX \
    && pip install --upgrade pip \
    && pip install pydoc-markdown pyyaml colored pandas matplotlib openpyxl