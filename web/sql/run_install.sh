ls ./install | xargs -i -n 1 sudo -u postgres psql -d icnml -a -f ./install/{}
