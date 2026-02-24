all: logdev

clean:
	-find . -name '*.pyc' -exec rm {} \;

updev:
	docker-compose up -d --build

logdev: clean updev
	docker-compose logs --tail=10 -f web

open:
	xdg-open http://localhost
	
down:
	docker-compose down

kill:
	docker-compose kill

update:
	git pull
	git submodule update

conf:
	cp -r ./config/keys ./web

fromtemplate:
	cat docker-compose.yml.template | envsubst > docker-compose.yml

build: conf fromtemplate
	docker-compose build --pull

push:
	docker push cr.unil.ch/icnml_web:${CI_COMMIT_SHORT_SHA}
	docker push cr.unil.ch/icnml_redis:${CI_COMMIT_SHORT_SHA}

app:
	-cd web/app; git checkout master; git merge develop; git push --all; git checkout develop;
	-echo "App update" > .git.message
	-echo "" >> .git.message
	-git diff --submodule=log web/app/ >> .git.message
	-git add web/app
	-git commit -F .git.message
	-rm .git.message
	-git push
	-git checkout develop

lib:
	-git submodule update --recursive --remote web/library/
	-echo "Lib update" > .git.message
	-echo "" >> .git.message
	-git diff --submodule=log web/library/ >> .git.message
	-git add web/library/*
	-git commit -F .git.message
	-rm .git.message
	-git push
	-git checkout develop

master:
	-git checkout master
	-git merge develop
	-git push
	-git checkout develop
