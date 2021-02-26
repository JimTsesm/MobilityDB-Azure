#!/bin/bash
sudo apt-get update
yes | sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
yes | sudo apt-get install docker-ce="5:18.09.0~3-0~ubuntu-bionic" docker-ce-cli="5:18.09.0~3-0~ubuntu-bionic" containerd.io