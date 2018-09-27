# HypDB Demo
To run the demo, first install Node, NPM, @angular/cli, pipenv, and python 3.6
```
# to start the server, first install dependencies with pipenv
cd server && pipenv install

# open a shell in your new pipenv virtual environment (inside the server directory)
pipenv shell

# also inside the server directory, run this inside your pip virtual environment
source ./env.sh

# then cd back into the root and run the server
npm run start-server

# (in another terminal window) to start the client, first install node_modules
cd client && npm i

# then cd back into the root and run the client
npm run start-client
```
