#!/bin/bash

# Get the directory name of the script
script_dir="$(pwd)"
main_dir="$(dirname "$script_dir")"

# This script is used to set up a development environment for the srt-fbo-scraper

if [uname -a | grep -q "Darwin"]; then
    echo "Detected Mac OS"

    # Mac
    # Check if curl is installed
    if ! command -v curl &> /dev/null
    then
        echo "curl could not be found"
        echo "Installing curl..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    fi

else
    echo "Detected Ubuntu" 

    # Check if curl is installed
    if ! command -v curl &> /dev/null
    then
        echo "curl could not be found"
        echo "Installing curl..."
        sudo apt-get install curl
    fi

fi 

# Install pyenv
if ! command -v pyenv &> /dev/null
then
    echo "pyenv could not be found"
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
fi

if [uname -a | grep -q "Darwin"]; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
    source ~/.bash_profile
else
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    source ~/.bashrc
fi



# Install python with pyenv
pyenv install 3.6 # TODO: Change to 3.10 when upgraded
pyenv global 3.6

# Create virtual environment
python -m venv $main_dir/venv

# Sourcing new virtual env
source $main_dir/venv/bin/activate

# Install requirements
pip install -r $main_dir/requirements.txt

# Symbolic link in site packages to fbo_scraper module
# TODO: Python > 3.6 solves this without symbolic link
# TODO: pip install -e $main_dir
cd $main_dir/venv/lib/python3.6/site-packages # Remove when > 3.6
ln -s $main_dir/fbo_scraper fbo_scraper # Remove when > 3.6
cd $main_dir
pip install .

# check if srt database exists
if [psql -l | grep "srt "] then
    echo "srt database exists"
else
    echo "srt database does not exist"
    
    # Create circleci User in postgresql
    sudo -u postgres createuser circleci
    sudo -u postgres psql -c "ALTER USER circleci WITH password 'srtpass';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO circleci;"
    sudo -u postgres psql -c "ALTER USER circleci WITH Superuser;"
    sudo -u postgres psql -c "ALTER USER circleci WITH CREATEROLE;"
    sudo -u postgres psql -c "ALTER USER circleci WITH CREATEDB;"

    # Create srt database
    echo "Creating srt database..."
    sudo -u postgres createdb srt -O circleci

fi

echo "Run fbo_scraper in cli to start scraper"
echo "Don't forget to set SAM_API_KEY & TEST_DB_URL environment variables for local run"
