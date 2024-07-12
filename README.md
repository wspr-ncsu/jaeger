# Jäger Prototype Implementation

This repository implements Jäger system's prototype.

This tutorial assumes you have read the paper and you are familiar with the key concepts

- Label generation using OPRF protocol
- Membership management using the group signature scheme
- BLS signatures and Witness Encryption based on these signatures.

## Before you start

For ease of setup, we will be setting up the project using docker. If you will be using docker then skip this section. If you prefer not to use docker then be sure your environment meets the following requirements:
- Python version 3.8.18
- Clickhouse DB
- Redis

The python dependencies are listed within the ```requirements.txt``` file. Install dependencies by running ```pip install -r requirements.txt```.  

This project also requires the witness-encryption library which you need to build from the repository https://github.com/kofi-dalvik/bls-witness-encryption. This library is already built and install for you if you're using docker. 
  
## Setup with Docker (RECOMMENDED)
You must make sure docker and docker compose are installed on your machine. 
1. Build the ```jager``` image from the ```Dockerfile```
	* Run ```docker build -t jager .``` 
	* Verify ```jager``` image exists by running ```docker image ls | grep jager```.
2. Generate secret key for label generation, group master and public keys for group management, private and public keys for BLS signatures and witness encryption.
	* Run ```docker run -v $(pwd):/app --rm jager python keygen.py -a```. The option ```-a``` tells the script to generate all keys. If you wish to generate keys for label generation only, use the ```-lm``` option. ```-gm``` option for group management, ```-ta``` for trace authorization/witness encryption. 
	* Verify that ```.env``` file is created and the variables are populated with appropriate keys. 
3. Start all Jager services: group manager, label manager, record store, trace authorizer, clickhouse database and redis server.
	* Run ```docker compose up -d```. This starts the services as defined within the ```compose.yml``` file. 
		* The Group management server runs on ```http://localhost:9990```. Implementation defined in ```app-gm.py```
		* The Label generation server runs on ```http://localhost:9991```. Implementation defined in ```app-lm.py```.
		* Trace authorization server runs on ```http://localhost:9992```. Implementation defined in ```app-ta.py```.
		* Record Store server runs on ```http://localhost:9993```. Implementation defined in ```app-rs.py```.

## Running Experiments
In this section, we will be running the prototype. We first begin with data generation then we run benchmarks to collect runtimes without communication latency between entities and finally, we run experiments where entities will communicate with one another. 

Our compose.yml file defines a ```jager-exp``` with all installed dependencies. We will be using this container to execute the experiments. 

### Data Generation
1. Login to the ```jager-exp``` container
	* Run ```docker exec -it jager-exp bash```
1. Generate telephone network. 

### Running Benchmarks
### Running Examples
