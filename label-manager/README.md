### Requirements
- Clickhouse v23.8.1
- Python v3.8.18
- Pip v23.0.1

### Initial Setup
- Create a copy:
    - of ```.env.example``` and save as ```.env```.
    - of ```.flaskenv``` and save as ```.flaskenv```
- Edit the variables in ```.env``` and ```.flaskenv``` to suit your case.
- Make service bash script executable (Optional): 
    - ```sudo chmod +x ./service```.
- Create Virtual Environment and Install dependencies: 
    - ```./service setup```. 
    This will automatically activate the venv for you.
- Create a database with same name as specified in your ```.env``` and run migrations: 
    - ```./service migrate```


## Start PrivyTrace Server Application
- Run: 
    - ```./service serve```. This starts the server and the insertion daemon.