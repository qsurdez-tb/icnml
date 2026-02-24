all: template deploy clean

template:
	cat docker-compose.yml.template | envsubst > docker-compose.yml

deploy:
	docker -H ${HOST} stack deploy -c docker-compose.yml icnml

clean:
	-rm ${CONFIGURATION}
