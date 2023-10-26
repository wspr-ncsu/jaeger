#!/bin/bash

valid_apps=(gm lm ta itg db)
valid_commands=(serve qw qs migrate)

app=$(echo $1 | cut -d ":" -f 1)
cmd=$(echo $1 | cut -d ":" -f 2)

function is_valid {
    local array=$1[@]
    local seeking=$2
    local in=1
    for element in "${!array}"; do
        if [[ $element == $seeking ]]; then
            in=0
            break
        fi
    done
    return $in
}

function migrate {
    echo "Running migrations for $app"
    python3.8 migrate.py
}

function run_app {
    app=$1
    if [ $app == "gm" ]
        then
        port=9990
    elif [ $app == "lm" ]
        then
        port=9991
    elif [ $app == "ta" ]
        then
        port=9992
    elif [ $app == "itg" ]
        then
        port=9993
    fi

    portInUse=$(sudo lsof -t -i:$port)

    if [ ! -z "$portInUse" ]
        then
        echo "Port $port is already in use. Killing process $portInUse..."
        sudo kill -9 $portInUse
    fi

    echo "Starting $app on port $port"
    python3.8 -m flask --app app-$app.py run --debug --port $port
}

function queue:stop {
    # if rq.pid.log does not exist, then a queue worker is not running
    if [ ! -f ./logs/rq.pid.log ]
        then
        echo "Queue worker is not running"
        exit 1
    fi
    
    echo "Stopping queue worker for traceback provider"
    kill $(cat ./logs/rq.pid.log)
    rm ./logs/rq.pid.log
}

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

if ! is_valid valid_apps $app; then
    echo "Invalid app: $app. Valid apps are: ${valid_apps[@]}"
    exit 1
fi

if ! is_valid valid_commands $cmd; then
    echo "Invalid command: $cmd. Valid commands are: ${valid_commands[@]}"
    exit 1
fi

if [ $cmd == "serve" ]
    then
    run_app $app
    exit 0
fi

if [ $app == "db" ]
    then
    if [ $cmd == "migrate" ]
        then
        migrate
    fi
    exit 0
fi

if [ $app == "itg" ]
    then
    if [ $cmd == "qw" ]
        then
        queue:work
    elif [ $cmd == "qs" ]
        then
        queue:stop
    fi
fi
