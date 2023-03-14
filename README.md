## Project Setup
- Create a copy of ```.env.example``` and save as ```.env```. Edit the variables to suit your case.
- Create a copy of ```.flaskenv``` and save as ```.flaskenv```. Edit the variables to suit your case.
- Make privytrace bash script executable: ```sudo chmod +x ./privytrace```.
- Create Virtual Environment and Install dependencies: ```./privytrace venv setup```. This will automatically activate the venv for you.
- Migrate database tables: ```./privytrace app migrate```

# Run Application
- Run: ```./privytrace app start```. This starts the server and the insertion daemon.