## Project Setup
### Requirements
- Clickhouse v23.8.1
- Python v3.7.9
- Pip v20.1.1

### Setup Steps
- Create a copy:
    - of ```.env.example``` and save as ```.env```.
    - of ```.flaskenv``` and save as ```.flaskenv```
- Edit the variables in ```.env``` and ```.flaskenv``` to suit your case.
- Make privytrace bash script executable: 
    - ```sudo chmod +x ./privytrace```.
- Create Virtual Environment and Install dependencies: 
    - ```./privytrace venv setup```. 
    This will automatically activate the venv for you.
- Create a database with same name as specified in your ```.env``` and run migrations: 
    - ```./privytrace app migrate```

## Start PrivyTrace Server Application
- Run: 
    - ```./privytrace app start```. This starts the server and the insertion daemon.

## CDR Generation
- To generate CDR datasets, run the command: ```./privytrace cdr generate```. This asks for number of carriers and subscribers.
- This command will generate a 
    - Phone network following bianconi-barabasi model 
	- Subscribers social network following the barabasi-albert model. Each edge within the social network represents a call endpoints of the edge.
-  The CDRs will be saved to a csv file


## Resources
- [Robocall Mitigation Database](https://fccprod.servicenowservices.com/rmd?id=rmd_welcome)