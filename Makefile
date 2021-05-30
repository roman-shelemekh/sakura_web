start:
	docker-compose up --remove-orphans

stop:
	docker-compose down --remove-orphans

psql:
	docker-compose exec db psql --username=sakura --dbname=sakura_dev

