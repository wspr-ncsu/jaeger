setup="setup"
serve="serve"
migrate="migrate"
deps="requirements.txt"

cmd=$1
allowed_commands=($setup $serve $migrate)

if [[ ! " ${allowed_commands[@]} " =~ " ${cmd} " ]]; then
    echo "Invalid command: $cmd. Valid commands are: ${allowed_commands[@]}"
    exit 1
fi

if [ $cmd == $setup ]
    then
    echo "Creating virtual environment"
    python3.8 -m venv .venv
    source ./.venv/bin/activate

    if test -f $deps; then
        echo "Installing requirements"
        pip install -r $deps
    fi
elif [ $cmd == $migrate ]
    then
    echo "Running migrations for traceback provider"
    source ./.venv/bin/activate
    python app.py migrate
elif [ $cmd == $serve ]
    then
    port=$2

    if [ -z "$port" ]
        then
        # get APP_PORT from .env file
        port=$(grep APP_PORT .env | cut -d '=' -f2)
    else
        # make sure port is between 10000 to 16999
        if [ $port -lt 10000 ] || [ $port -gt 16999 ]
            then
            echo "Error: Port must be between 10000 to 16999 for a provider"
            exit 1
        fi
    fi

    echo "Starting Network Provider on port $port"
    source ./.venv/bin/activate
    flask run --port $port
fi