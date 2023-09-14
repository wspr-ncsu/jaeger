# Network Provider
The network provider is a carrier in the network and implement the call and trace stages of the protocol. 

They 
- Register with Group Manager to receive group key and member secret key
- Register with label Manager to receive Kprf
- Register with Trace Authority to receive signature verification keys (public) for the scheme.
- Route calls between subscribers
- Generate CDR records and submit it to traceback-provider following the trace protocol


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