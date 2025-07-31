# How to use
## Step 1: Clone the project

```bash
git clone https://github.com/minhnn2002/fastapi.git
```

Then cd to the main project
```bash
cd fastapi
```

## Step 2: Create the .env file
This file contains your private information needed to connect to the database:
- DB_USER: The username
- DB_PASSWORD: The password
- DB_HOST: The domain name of database
- DB_PORT: The port to connect
- DB_DATABASE: The database name

## Step 3: Run the project on Docker. (If you deploy on k8s, skip to the next step)
To run the project on Docker, simply run the command 
```bash
docker compose up -d
```

Then go to the 
```bash
http://localhost:8000/docs
```
to check the available API

## Step 4: Deploy the project on K8S
First fill the file k8s/secret.yaml. It has the same content like the .env file. Every information must be in the "" bracket.
I'm using minikube to run so first start the minikube
```bash
minikube start --driver=docker
```

Then check the status
```bash
minikube status
```

If everything is fine, then move to the k8s folder:

```bash
cd .\k8s\
```

Deploy the minikube cluster:

```bash
kubectl apply -f ./.
```

Finally use the following command to create the service to connect to API:
```bash
minikube service fastapi-serivce
```