# Label Manager
The label manager manages labels for calls. It exposes few endpoints to handle the following:

- ```/register```: Carriers hit this endpoint to retrieve the Kprf


### Requirements
- Python v3.8.18 and Pip v23.0.1
- Redis Server

### Initial Setup
- Create a copy:
    - of ```.env.example``` and save as ```.env```.
    - Modify the variables in ```.env``` to suit your case.
- Make service bash script executable (Optional): 
    - ```sudo chmod +x ./service```.
- Create Virtual Environment and Install dependencies: 
    - ```./service setup```


### Start Service
- Run: 
    - ```./service serve```. This starts the server.