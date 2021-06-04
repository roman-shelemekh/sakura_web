start:
	docker-compose up --remove-orphans

stop:
	docker-compose down --remove-orphans

db-migrate:
	docker-compose exec sakura flask db migrate

db-upgrade:
	docker-compose exec sakura flask db upgrade

psql:
	docker-compose exec db psql --username=sakura --dbname=sakura_dev

shell:
	docker-compose exec sakura flask shell

psql-prod:
	docker-compose exec db psql --username=sakura --dbname=sakura_prod

start-prod:
	docker-compose -f docker-compose.prod.yml up --build --remove-orphans

stop-prod:
	docker-compose -f docker-compose.prod.yml down --remove-orphans

db-prod:
	docker-compose -f docker-compose.prod.yml exec sakura flask db upgrade

