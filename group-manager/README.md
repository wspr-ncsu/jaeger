# Group Manager
The group manager (GM) manages the group signature scheme. The GM sets up the scheme, and registers phone providers as members

- ```/register```: Carriers hit this endpoint to retrieve the Kprf
- ```/deanonymize```: Opens a ciphertext to recover the identity of the encrypter


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


## Start Service
- Run: 
    - ```./service serve```. This starts the server.