# International Close Non-Matches Library - ICNML

This GIT repository is the main repository to build all the parts of ICNML.

All parts are assembled using GIT submodules (web application and all the mandatory libraries).

The CICD is in charge of building the ICNML application, and make the commits to the configurations repository (https://esc-md-git.unil.ch/ICNML/conf/production).
This repository will not deploy to production, but will commit to the correct repositories, triggering the CICD automatic deployment.

This docker-compose file is not designed to be run in development or production mode, but only by the GitLab CICD.
The Makefile is not intended to be run manually here for development of production, but only used by the CICD to build and push to staging and production.
Check the production GIT module (https://esc-md-git.unil.ch/ICNML/conf/production) to see the production configuration.

To download the entire code-base, go to https://esc-md-git.unil.ch/ICNML/docker and git clone the repository.
The download link on gitlab doesn't sync the submodules needed to build the ICNML application.

# Installation of the development version

To install the development version, clone the `docker` repository with the `--recursive` option, create the `env` file (check the example below) and start all the containers with the `docker-compose` command.
One database should be provided to the script to be able to start; either use a backup of the production database, or create an empty one with the `.sql` files available in this git repository.

The is a configuration file usable for dev purposes:

```
DB_URL=pgsql://postgres:icnml@db/icnml
DEBUG=True
ENVTYPE=dev
REDIS_URL=redis://redis:6379/0
REDIS_URL_SHARED=redis://redis:6379/1
SESSION_TIMEOUT=3600
```

If the database is imported from the production backup, don't forget to import the `data` and `dek` backup files.
If you don't import the `dek` file, the ICNML server will start, but the images will not be loadable ("no preview" will be displayed instead).

