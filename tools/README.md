This repo contains mutliple scripts used as tooling (migration and extraction of data, conversion, ...).

Be aware that the scripts are not made to be run as-is; be smart, read the code and adapt it as you need in your particular case.

It contains the link (as submodules) to the remote libraries needed to run the scripts; a `git clone` with the `--recursive` option has to be done to initialize the submodules as needed.

To run the scripts in this repo, we have to create a python virtual environment:

```
virtualenv -p /usr/bin/python2 venv

```

activate it

```
source venv/bin/activate
```

and install the required packages:

```
find . -name 'requirements.txt' -exec pip install -r {} \;
find . -name "requirements.txt" -exec realpath {} \; | xargs -n 1 dirname > $(find . -name 'site-packages')/mdedonno.pth
```

The environment should be ready to be run with a `python` command.

It's also possible to build the current directory with docker to have a Debian image with all the tools installed.
To do so, check the content of the Makefile to see the docker compilation commands.

