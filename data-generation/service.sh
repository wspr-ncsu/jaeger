setup="setup"
generate="generate"
deps="requirements.txt"

cmd=$1
allowed_commands=($setup $generate)

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
elif [ $cmd == $generate ]
    then
    echo "Generating CDR datasets"
    source ./.venv/bin/activate

    num_carriers=$2
    num_subs=$3

    if [ -z $num_carriers ]
        then
        num_carriers=7000
    fi

    if [ -z $num_subs ]
        then
        num_subs=1000000
    fi

    python ./generator.py -c $num_carriers -s $num_subs
fi