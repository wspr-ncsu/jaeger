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
In this section, we will see how to generate the telephone network, users network and viewing generated data. 

1. **Login to the ```jager-exp``` container**
	* Run ```docker exec -it jager-exp bash```
2. **Generate telephone and users' social network** 
	* First run help ```python datagen.py -h``` to display usage information.
	* Command: ```python datagen.py [-h] [-n NETWORK] [-s SUBSCRIBERS] [-g SUBNETS] [-c] [-y]```. 
		* The options ```-n``` and ```-s``` take integers as values and defines the number of providers in the telephone network and number of subscribers in the social network respectively.  
		* The users network is a network of network thus the option ```-g``` specifies the minimum number of subsnetworks that should be present in the users network.  
		* Option ```-c``` determines if CDRs should be generated and ```-y``` determines if yes will be selected for any question. 
    * Let's generate CDRs with 100 providers and 10,000 subscribers:
        * Run ```python datagen.py -n 100 -s 10000 -c -y```. This generates and stores cdrs in the clickhouse database ```jager```.  
	        * The edges of the user network is stored in ```jager.edges``` table and generated CDRs are stored in ```jager.raw_cdrs``` table.
	   * The telephone network and it's metadata such as all pairs shortest paths and marketshares are stored as a python pickle in a ```cache.pkl``` file located at the project root. The essense of this is to allow us reuse a generated network since generating network is randomized. 
3. **View Generated dataset**
	* We added a UI service that allows you to connect to the database. Visit ```http://localhost:5521```. 
		* Enter ```http://localhost:8123``` as Clickhouse URL, ```default``` as Username and ```secret``` as Password and click the ```Submit``` button. Once successful, click on ```Go back to the home page.``` link. 
		* On the home page, select ```Jager``` in the databases field and this will load the tables. Now you can click on any table to view table Details, Scheme or Preview rows. 
		* If you prefer to run your own SQL querries, then click on the new file icon/button with the orange background. Type in ```select * from jager.raw_cdrs limit 10;``` in the query field and click the "Run Query" button. 

### Running Benchmarks
The results from Table 3, were obtained by running the benchmarks. These benchmarks determine runtime for label generation, signing and verification, key generation, encryption and decryptions.  

### Running Examples
