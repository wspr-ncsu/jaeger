queue_work="queue:work"
queue_stop="queue:stop"
queue_restart="queue:restart"

serve="serve"
migrate="migrate"
deps="requirements.txt"

cmd=$1
allowed_commands=($serve $migrate $queue_work $queue_stop $queue_restart)

function queue:work {
    # if rq.pid.log exists, then a queue worker is already running
    if [ -f ./logs/rq.pid.log ]
        then
        echo "Queue worker is already running. Logs are in ./logs/rq.wrk.log"
        exit 1
    fi
    echo "Starting queue worker for traceback provider"
    touch ./logs/rq.pid.log
    rq worker --with-scheduler --pid ./logs/rq.pid.log > ./logs/rq.wrk.log 2>&1 &
    echo "Queue worker started. Logs are in ./logs/rq.wrk.log"
}

function queue:stop {
    echo "Stopping queue worker for traceback provider"
    kill $(cat ./logs/rq.pid.log)
    rm ./logs/rq.pid.log
}

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

    flask run --debug --port $port
elif [ $cmd == $queue_work ]
    then
    queue:work
elif [ $cmd == $queue_stop ]
    then
    queue:stop
elif [ $cmd == $queue_restart ]
    then
    queue:stop 
    queue:work
fi