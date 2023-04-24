## Project Setup
### Requirements
- Postgres
- Python 3

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
- Migrate database tables: 
    - ```./privytrace app migrate```

## Run Application
- Run: 
    - ```./privytrace app start```. This starts the server and the insertion daemon.

## Run Demo
While the application is running you can run demo. This initiates fake calls and make contribution requests to the api to save call records. The ```demo/run.py``` file serves this purpose. 

To Run demo, run the command ```./privytrace demo```. This will log details of each call in a file with filename format: ```src_dst_ts.log``` in ```demo/logs/``` folder. You will use this data for querying traces.

Example of contents of the ```.log``` file for a call is given below:
```
src_tn	=	410-592-8094 (blue_sky)
dst_tn	=	581-209-1986 (mint_mob)
call_ts	=	1679578836
hops	=	blue_sky -> cellcom -> blue_wireless -> mint_mob

blue_sky
	cci	=	410-592-8094:581-209-1986:1679578836
	tbc	=	None|blue_sky|410-592-8094:581-209-1986:1679578836
	tfc	=	blue_sky|cellcom|410-592-8094:581-209-1986:1679578836

cellcom
	cci	=	410-592-8094:581-209-1986:1679578836
	tbc	=	blue_sky|cellcom|410-592-8094:581-209-1986:1679578836
	tfc	=	cellcom|blue_wireless|410-592-8094:581-209-1986:1679578836

blue_wireless
	cci	=	410-592-8094:581-209-1986:1679578836
	tbc	=	cellcom|blue_wireless|410-592-8094:581-209-1986:1679578836
	tfc	=	blue_wireless|mint_mob|410-592-8094:581-209-1986:1679578836

mint_mob
	cci	=	410-592-8094:581-209-1986:1679578836
	tbc	=	blue_wireless|mint_mob|410-592-8094:581-209-1986:1679578836
	tfc	=	mint_mob|None|410-592-8094:581-209-1986:1679578836
```
which shows the records contributed by each provider. i.e ```cci```, ```tbc```, and ```tfc```

Once the demo is completed, you can perform trace queries using the commands:
- Traceback: ```./privytrace traceback {tbc}```, where ```{tbc}``` will be replaced with the traceback component from the log
- Traceforward: ```./privytrace traceforward {tfc}``` where ```{tfc}``` will be replaced with the trace forward component from the log
- Lookup: ```./privytrace lookup {cci}``` where ```{cci}``` will be replaced by the cci from the log

You can then compare the returned response from these commands to the respective call log for correctness.


## Resources
- [Robocall Mitigation Database](https://fccprod.servicenowservices.com/rmd?id=rmd_welcome)