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
## Copy all the files (Don't change layout)
### Lets say that your layout is /SteamScraper

## Start a local Docker registry:
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    
## Set the Minikube Docker environment
    eval $(minikube -p minikube docker-env)
    
## Tag the images
    docker tag interface:latest localhost:5000/interface:latest
    docker tag engine:latest localhost:5000/engine:latest
    
## Make Docker image for engine
    cd /SteamScrapper/engine
    docker build -t localhost:5000/engine:latest .
    docker push localhost:5000/engine:latest

## Make Docker image for interface
    cd /SteamScrapper/interface
    docker build -t localhost:5000/interface:latest .
    docker push localhost:5000/interface:latest

## Apply the Kubernetes configuration files:
    kubectl apply -f /SteamScrapper/kubernetes/engine-deployment.yaml
    kubectl apply -f /SteamScrapper/kubernetes/interface-deployment.yaml
    kubectl apply -f /SteamScrapper/kubernetes/mongodb-deployment.yaml

## Check the pods status (all should be running)
    kubectl get pods

# Known Errors
## MongoDB pulls the wrong version (Above 5.0)
### Manually Pull the MongoDB 4.4 Image
    minikube ssh
    docker pull mongo:4.4
    exit

# Access the service
## Get Minikube ip
    #There should be ip address which you can use to access the service (mine example: 192.168.49.2)
## Get service port
    kubectl get services
    #There should be your interface-service with the port. It should always be 32256 but in case it isn't (even after being specified in .yaml file) use the one that shows.
## Access the website
    #In you browser write minikubeip:interface-service port (For me it was 192.168.49.2:32256)

# Clearing MongoDB
## Get name of the MongoDB pod
    kubectl get pods
## Access it and drop the database
    #Lets say that your pod name is mongodb-deployment-9f549b7b6-clzp8
    kubectl exec -it mongodb-deployment-9f549b7b6-clzp8 -- /bin/bash
    mongo
    show databases
    use steam_scraper
    db.dropDatabase()
    exit
    exit
