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
elif [ $cmd == $serve ]
    then
    port=$2

    if [ -z "$port" ]
        then
        # get APP_PORT from .env file
        port=$(grep APP_PORT .env | cut -d '=' -f2)
    fi

    if [ -z "$port" ]
        then
        port=9997
    fi

    echo "Starting Group Manager on port $port"
    source ./.venv/bin/activate
    flask run --port $port
fi