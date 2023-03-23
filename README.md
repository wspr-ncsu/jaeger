## Project Setup
- Create a copy:
    - of ```.env.example``` and save as ```.env```.
    - of ```.flaskenv``` and save as ```.flaskenv```
    Edit the variables to suit your case.
- Make privytrace bash script executable: 
    - ```sudo chmod +x ./privytrace```.
- Create Virtual Environment and Install dependencies: 
    - ```./privytrace venv setup```. 
    This will automatically activate the venv for you.
- Migrate database tables: 
    - ```./privytrace app migrate```

# Run Application
- Run: ```./privytrace app start```. This starts the server and the insertion daemon.

# Run Demo
While the application is running you can run demo. This initiates fake calls and make contribution requests to the api to save call records. The ```demo.py``` file serves this purpose. 

To Run demo, run the command ```./privytrace demo```. This will log some details  in ```demo.log``` which you will use for querying traces.

Once the demo is completed, you can perform trace queries using the commands:
- Traceback: ```./privytrace traceback {tbc}```, where ```{tbc}``` will be replaced with the traceback component from the log
- Traceforward: ```./privytrace traceforward {tfc}``` where ```{tfc}``` will be replaced with the trace forward component from the log
- Lookup: ```./privytrace lookup {cci}``` where ```{cci}``` will be replaced by the cci from the log