### Requirements
- Python v3.8.18
- Pip v23.0.1

### Initial Setup
- Make service bash script executable (Optional): 
    - ```sudo chmod +x ./service```.
- Create Virtual Environment and Install dependencies: 
    - ```./service setup```. 
    This will automatically activate the venv for you.
- Create a database with same name as specified in your ```.env``` and run migrations: 
    - ```./service migrate```


### Run Data Generation
- Run: 
    - ```./service generate {num_carriers} {number_subscribers}```.
        - ```{num_carriers}``` is the desired number of carriers, default is 7,000
        - ```{number_subscribers}``` is the desired number of subscribers, default is 1,000,000