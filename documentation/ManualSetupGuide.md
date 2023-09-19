# Manual Setup Guide 
Use the following as a guide to install required modules when the automated setup script fails or is not available. 

* First, navigate to the root level of the folder for your project. 
* Next, execute the following commands according to your operating system: 

## Install curl 
Mac: 
```
echo "Installing curl..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

Ubuntu: 
```
echo "Installing curl..."
sudo apt-get install curl
```
## Install pyenv 
For both Mac and Ubuntu: 
```
echo "Installing pyenv..."
curl https://pyenv.run | bash
```

* Navigate to the desired folder to clone the srt-fbo-scraper project. 
* Then execute the following in the command line: 
* Replace `<your main project folder>` below with the actual path to the root level of your project. 

Mac: 
```
echo 'export PYENV_ROOT="<your main project folder>/.pyenv"' >> ~/.bash_profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
```

Ubuntu: 
```
echo 'export PYENV_ROOT="<your main project folder>/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```
## Install python with pyenv
For both Mac and Ubuntu: 
```
pyenv install 3.6 
pyenv global 3.6
```

## Create the virtual environment
```
python -m venv <your main project folder>/venv
```
## Source the new virtual env
```
source <your main project folder>/venv/bin/activate
```
## Install requirements
```
pip install -r <your main project folder>/requirements.txt
```
## Symbolic link in site packages to fbo_scraper module
```
cd <your main project folder>/venv/lib/python3.6/site-packages 
ln -s <your main project folder>/fbo_scraper fbo_scraper 
cd <your main project folder>
pip install .
```
## Download SRT Source Code 
For both Mac and Ubuntu: 
* Navigate to the desired folder to clone the srt-fbo-scraper project. 
* Then execute the following in the command line: 
```
git clone https://github.com/GSA/srt-fbo-scraper.git
cd srt-fbo-scraper
git checkout dev
npm install
```

## Create the Postgres User 
```
sudo -u postgres createuser circleci
sudo -u postgres psql -c "ALTER USER circleci WITH password 'srtpass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO circleci;"
sudo -u postgres psql -c "ALTER USER circleci WITH Superuser;"
sudo -u postgres psql -c "ALTER USER circleci WITH CREATEROLE;"
sudo -u postgres psql -c "ALTER USER circleci WITH CREATEDB;"
```

## Create the SRT database
```
echo "Creating srt database..."
sudo -u postgres createdb srt -O circleci
```

## Set Environment Variables 
Make sure to set the following environment variables: 
* SAM_API_KEY
* TEST_DB_URL