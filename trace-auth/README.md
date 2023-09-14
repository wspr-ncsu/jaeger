# Trace Authority
The trace authority issues signatures for traces to be carrier out. Without signing a trace by the trace authority, ciphertexts cannot be decrypted

- ```/register```: Carriers hit this endpoint to retrieve the public verification key


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


## Start PrivyTrace Server Application
- Run: 
    - ```./service serve```. This starts the server.