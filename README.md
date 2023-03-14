## Project Setup
- Create a copy of ```.env.example``` and save as ```.env```. Edit the variables to suit your case
- Create a virtual environment ```venv``` with the command ```python3 -m venv venv```. This should insert a ```venv``` folder into the project root.
- Activate the virtual environment by running the activate command: ```. venv/bin/activate```.
- Install dependencies: ```pip install -r requirements.txt```
- Run migrations for the tables to be created in postgres: ```flask --app app migrate```
- Run queue worker: ```rq worker <REQUEST_QUEUE>``` where ```<REQUEST_QUEUE>``` should be replaced by the value in ```.env``` you created in first step.
- Start the server: ```flask run```. Note that this will use configurations defined inside ```.flaskenv``` to run the flask project. 