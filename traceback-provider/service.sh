serve="serve"
migrate="migrate"
deps="requirements.txt"

cmd=$1
allowed_commands=($serve $migrate)

if [[ ! " ${allowed_commands[@]} " =~ " ${cmd} " ]]; then
    echo "Invalid command: $cmd. Valid commands are: ${allowed_commands[@]}"
    exit 1
fi

if [ $cmd == $migrate ]
    then
    echo "Running migrations for traceback provider"
    python3.8 migrate.py
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
        port=9993
    fi

    echo "Starting Traceback provider on port $port"

    portInUse=$(sudo lsof -t -i:$port)

    if [ ! -z "$portInUse" ]
        then
        echo "Port $port is already in use. Killing process $portInUse..."
        sudo kill -9 $portInUse
    fi

    flask run --port $port
fi