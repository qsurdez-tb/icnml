all: dev

dev: dockerfile build

dockerfile:
	cat Dockerfile | \
	    sed -e '/^ENTRYPOINT/d' | \
	    sed -e 's/^WORKDIR \/app/WORKDIR \/code/g' > Dockerfile.dev

build: dockerfile
	docker build -t icnml -f Dockerfile.dev .

