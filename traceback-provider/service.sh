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
    echo "Starting traceback provider server"
    source ./.venv/bin/activate
    flask run
fi