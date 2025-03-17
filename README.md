[![All Tests](https://github.com/Busig-The-SQL/Busig/actions/workflows/main.yml/badge.svg)](https://github.com/Busig-The-SQL/Busig/actions/workflows/main.yml)

# CS3305-2025-Team-10: Busig

Team Software Project for the CS3305 module

## How to Deploy Containers Locally
>
> Build, run containers using docker compose and create the database

### Getting the containers

- The containers are currently not finished, so we are not using the docker hub which is the standard way of distributing images
- Instead you need to pull the code from github like so:

```bash
git checkout main
git pull origin main
```

- Now you should navigate to the root of the Project, the file called `docker-compose.yml` should be there.

### Configuring .env

- The containers rely on a file called `.env` existing in the same directory as `docker-compose.yml`
- This file contains the api key for GTFS api (The real time bus data)
- The file cannot be put on github because it would be compromised, the method of distribution is just manual now, so you need to create this file in your project root

### Running docker containers

- Docker needs to be installed, run `docker -v` to check it is running on your system
- First the containers need to be build and then run (building takes 16 min, but running them is 5 mins for the first time, then <2 min after, depends on device specs)

```bash
docker compose build
docker compose up
```

- you can also use the `-d` flag to run the containers in the background with `docker compose up` however I recommend omitting it as it is useful for debugging
- Now the containers should run, you can check the containers running with `docker ps`
- If you want to stop them, either pres `^C` in the terminal or run `docker compose down`
- If this step failed, then there is most likely issue with the code and ask Radek about it

### Building the database

- The first time the containers are ran, the database will be built. This usually takes 5+ mins, but only will happen on the first run. If the database needs to be updated in the future, you can run the script by itself as below.

```bash
docker exec -t bus_model bash scripts/update_GTFS_Static.sh
```

- This will fetch the latest zip file containing the information about the buses, unzips it and creates a Postgresql db with it
- The only information in the db should be about the routes we care about

#### How it works

- There is a container called `postgres`, this one is the official docker image from postgres, it essentially just serves as a DBMS
- The code to actually write into the database is located in the container `bus_model`, this code talks to the other container
- The postgres still is located on your system in a custom folder defined in `docker-compose.yml` and it persists!
- This means that if you build the db once, it stays on your system even after you run `docker compose down`
- Therefore you need to run this code just once and then only again if you want it updated, the same is true for mongodb
- Since there is a lot of data, the creation, filtering, indexing, etc. takes ~5 mins to complete, depends on the system, etc.

### Running code inside the cotnainers

- You can run the code inside the containers, but first you need to access them using this command:

```bash
docker exec -it <container_name> bash
```

- `-i` means interactive, so instead of running a specified command, it just opens the bash console in the specified container
- exit the container with `exit`
- If you want to execute just one command, you can run this

```bash
docker exec -t <container-name> <command>
docker exec -t example_container python3 example.py
```

- Please use this method to test your code, it generates some overhead because you need to access the containers, but it is much cleaner
- Once the code runs inside the container on your system and all the code is pushed, then it should work for everyone!

### Accessing the api of the container

- The containers are reachable from the outside only through flask endpoints in our app, all of the containers will run a flask server listening on different ports

|Container|Port|
|--|--|
|`training_data_collection`|5000|
|`inference`|5001|
|`bus_model`|5002|
|`gateway`|5004|

- The uri to access them are written inside environment variables available in the containers, check `docker-compose.yml` if you want more info

#### Accessing gateway from frontend

- As a relevant example, here is the url to access gateway flask api which would be used for development while the containers are running on your system

```bash
http://localhost:5004/<endpoint>
```

- Eventually this will be employed on the home server, than the url will be nearly completed different because of NAT
