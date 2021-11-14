#!/bin/bash

wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key|sudo apt-key add -
sudo add-apt-repository 'deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-13 main' -y

sudo apt-get update -q

sudo apt-get install \
  g++-6 \
  gcc-multilib \
  libc6-dev-i386 \
  libpq-dev \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  clang-13 \
  clang-tidy-13

sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-13 9999
sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-13 9999
sudo update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-13 9999
