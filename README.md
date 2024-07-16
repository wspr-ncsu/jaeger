# Jäger Prototype Implementation

This repository implements Jäger system's prototype.

This tutorial assumes you have read the paper and you are familiar with the key concepts

- Label generation using OPRF protocol
- Membership management using the group signature scheme
- BLS signatures and Witness Encryption based on these signatures.

## Initial Project Setup

For ease of setup, we will be setting up the project using docker. If you prefer not to use docker then read along otherwise skip to Setup with Docker section.

### Setup without Docker
Be sure your environment meets the following requirements:
- Python version 3.8.18
- Clickhouse DB (Clickhouse server and client to connect to the server)
- Redis

**Dependencies**
The python dependencies are listed within the ```requirements.txt``` file. Install dependencies by running ```pip install -r requirements.txt``` in a python virtual environment.  

This project requires the witness-encryption library which you need to build from the repository https://github.com/kofi-dalvik/bls-witness-encryption. We created ```install-witenc.sh``` file to install this library for you if you will not be using docker. 

**Database Initialization**
Once you setup Clickhouse DB, create the jager table and initialize the database with init script in ```docker/clickhouse/initdb.sql```.

**Quick app setup**
Generate keys with ```python keygen.py -a```. This creates .env file with populated data.
  
### Setup with Docker (RECOMMENDED)
You must install docker and docker compose on your machine. 

1. Generate secret key for label generation, group master and public keys for group management, private and public keys for BLS signatures and witness encryption.
	* Run ```docker run -v $(pwd):/app --rm kofidahmed/jager python keygen.py -a```. 
	* The option ```-a``` tells the script to generate all keys. 
	* If you wish to generate keys for label generation only, use the ```-lm``` option. ```-gm``` option for group management, ```-ta``` for trace authorization/witness encryption. 
	* Verify that ```.env``` and ```membership-keys.json``` files are created and the variables are populated with appropriate keys. 
3. Start all Jager services: group manager, label manager, record store, trace authorizer, clickhouse database and redis server.
	* Run ```docker compose up -d```. 
		* The Group management server runs on ```http://localhost:9990```. Implementation defined in ```app-gm.py```
		* The Label generation server runs on ```http://localhost:9991```. Implementation defined in ```app-lm.py```.
		* Trace authorization server runs on ```http://localhost:9992```. Implementation defined in ```app-ta.py```.
		* Record Store server runs on ```http://localhost:9993```. Implementation defined in ```app-rs.py```.

## Running Experiments
In this section, we will be running the prototype. We first begin with running benchmarks to collect runtimes without communication latency between entities and finally, we run dataset generation and experiments where entities will communicate with one another. 

Our ```compose.yml``` file defines a ```jager-exp``` with all installed dependencies. We will be using this container to execute the experiments. 


### Running Experiment 1 - Benchmarks
The results from Table 3, were obtained by running the benchmarks. These benchmarks determine runtime for label generation, signing and verification, key generation, encryption and decryptions.
  
1. If using docker, run ```docker exec -it jager-exp bash``` if you're not already inside ```jager-exp``` container.
2. Command Usage: ```python benchmarks.py [-h] [-s] [-lg] [-gs] [-go] [-gv] [-a] [-b] [-e] [-ah] [-an]```. Here are the options
	* ```-s```, or ```--setup```:  Run setup/key generation benchmark
    * ```-lg```, or ```--lbl_gen```: Run label generation benchmark
    * ```-gs```, or ```--grp_sign```:  Run group signature benchmark
    * ```-go```, or ```--grp_open```: Run group signature open benchmark
    * ```-gv```, or ```--grp_verify```: Run group verification benchmark
    * ```-a```, or ```--all```: Run all benchmarks
    * ```-b```, or. ```--bls```:  Run BLS signature benchmark
    * ```-e```, or ```--enc```: Run encryption benchmark
    * ```-ah```, or ```--hops```: Run average number of hops
    * ```-an```, or ```--analysis```: Run analysis
3. Example run for key generation benchmark
	* Run ```python benchmarks.py --setup```.  This will display the results to console and will create a ```results``` folder inside the project root. 
		* ```results/bench.csv``` contains the aggregated benchmarks while ```results/index-timings.csv``` contains the individual runs. We used ```results/index-timings.csv``` to determine the mean, min, max and standard deviations. 

### Running Experiment 2
In experiment 2, we generate a telephone network and users social network. We simulated calls between users and created CDRs for running experiments. In this experiment, we aim to determine bandwidth,  storage growth and how storage size affects queries as show in Figure 6.

#### Data Generation
1. Run ```docker exec -it jager-exp bash``` if not already in ```jager-exp``
2. Generate telephone and users' social network 
	* Command Usage: ```python datagen.py [-h] [-n NETWORK] [-s SUBSCRIBERS] [-g SUBNETS] [-c] [-y]```. 
		* The options ```-n``` and ```-s``` take integers as values and defines the number of providers in the telephone network and number of subscribers in the social network respectively.  
		* The option ```-g``` specifies the minimum number of subsnetworks that should be present in the users network.  
		* Option ```-c``` determines if CDRs should be generated and ```-y``` skips all questions.
    * Exaple, let's generate CDRs with 100 providers and 10,000 subscribers:
        * Run ```python datagen.py -n 100 -s 10000 -c -y```. This stores cdrs in the clickhouse database ```jager```.  
	        * The edges of the user network is stored in ```jager.edges``` table and generated CDRs are stored in ```jager.raw_cdrs``` table.
	   * The telephone network and it's metadata such as all pairs shortest paths and marketshares are stored as a python pickle in a ```cache.pkl``` file located at the project root. The essense of this is to allow reusage of generated network data since the operation is randomized. 
3. **View Generated dataset**
	* We added a UI service that allows you to connect to the database. Visit ```http://localhost:5521```. 
		* Enter ```http://localhost:8123``` as Clickhouse URL, ```default``` as Username and ```secret``` as Password and click the ```Submit``` button. Once successful, click on ```Go back to the home page.``` link. 
		* On the home page, select ```Jager``` in the databases field and this will load the tables. Now you can click on any table to view table Details, Scheme or Preview rows. 
		* If you prefer to run your own SQL querries, then click on the new file icon/button with the orange background. Type in ```select * from jager.raw_cdrs limit 10;``` in the query field and click the "Run Query" button. 

#### Running Contributions
1. Run ```docker exec -it jager-exp bash``` if not already in ```jager-exp```
2. Command Usage: ```python run-contribution.py [-h] [-b BATCHES] -r RECORDS [-c]```
	* Arg ```-b``` takes the number of batches. This is the number of times you wish to run the contribution experiment. It default to ```1```. After each batch, database stats are measured and stored in ```results``` folder. 
		* Arg ```-r``` takes the number of records in a batch. This is the number of records to submit. This arg is required. 
	* Let's run contributions for 3 batches with 100 records in a batch:
		* Run ```python run-contribution.py -b 3 -r 100```. This saves the results in ```results/db_stats.csv``` and ```results/queries.csv```.


#### Run a Traceback (Optional)
Now let's perform a traceback by querying for a call that has been submitted to the RS.
1. Visit ```http://localhost:8123``` and execute the SQL ```select src, dst, ts from jager.raw_cdrs where status =  1;```. The results from this query are the calls whose ciphertexts have been submitted to the RS. 
2. If not already logged in, run ```docker exec -it jager-exp bash```.
3. Trace a call given ```(src, dst, ts)```
	* Run ```python run-trace.py -s src -d dst -t ts```. Replace ```src, dst, ts``` with actual values from the results in step 1. 
	* Example: ```python run-trace.py -s 304-343-0688 -d 844-637-3806 -t 1721076561```. This command will:
		1. Will generate call labels within [ts - tmax, ts + tmax] range
		2. Request authorization signatures from TA
		3. Retrieve ciphertexts from the RS
		4. Decrypt and analyze the records to determine the origin and call path. 
