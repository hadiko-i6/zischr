#!/bin/bash

set -ex

cd "$(dirname ${BASH_SOURCE[0]})"

PROJECTROOT="../.."
INSTALLDIR="/zischr"

cd "$PROJECTROOT"

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y --no-install-recommends \
    python3-pyqt5 \
    python3-pip \
    python3-dev \
    build-essential \
    python3-serial \
    git \
    xinit \
    xinput \
    rsync \
    wget \
    coreutils

pip3 install grpcio


pushd "$HOME"
GODL='go1.9.3.linux-armv6l.tar.gz'
if [ ! -f "$GODL" ]; then
        wget "https://dl.google.com/go/${GODL}"
        sha256sum "$GODL" | grep '926d6cd6c21ef3419dca2e5da8d4b74b99592ab1feb5a62a4da244e6333189d2'
        tar -x -C /usr/local -f "$GODL"
fi
export PATH="/usr/local/go/bin:$PATH"
popd

export GOPATH=${GOPATH:-"$HOME/go"}
go get -u github.com/golang/dep/cmd/dep


pushd backend
mkdir -p "$GOPATH/src/github.com/hadiko-i6/zischr"
ln -sf "$(readlink -f .)" "$GOPATH/src/github.com/hadiko-i6/zischr/backend"
pushd "$GOPATH/src/github.com/hadiko-i6/zischr/backend"
$GOPATH/bin/dep ensure
popd
popd

make deploy DEPLOYDIR="${INSTALLDIR}"

install -m 755 deployment/raspi3/frontend.sh ${INSTALLDIR}/frontend.sh
install -Dm 644 deployment/raspi3/zischr*.{target,service} /etc/systemd/system/

systemctl daemon-reload

systemctl enable /etc/systemd/system/zischr*.{target,service}
systemctl restart zischr.target
