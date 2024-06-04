# SteamScrapper
SteamScrapper for a school project. It offers basic way of <a href="https://store.steampowered.com/">searching steamstore</a> using written by user categories in input.
# Prerequisites
* Have Docker installed: You can find more info here: https://docs.docker.com/engine/install/
* Have Kubernetes installed: You can find more info here: https://kubernetes.io/releases/download/
# How to install (example for Ubuntu Linux machine using minikube)
##  Install docker (If not installed)
### Set up Docker's apt repository.
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    
    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update  
 ### Install the Docker packages
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
 ### Verify that the Docker Engine installation is successful by running the hello-world image.
    sudo docker run hello-world
## Install kubernetes (If not installed)
    snap install kubectl --classic
    kubectl version --client
## Install minikube (If not installed)
### Installation
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
### Start your cluster
     minikube start
##
