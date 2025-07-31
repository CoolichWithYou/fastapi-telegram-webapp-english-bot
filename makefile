.PHONY: lint test install

SRC=. tests

lint:
	@echo "Running isort..."
	cd server && isort $(SRC)

	@echo "Running black..."
	cd server && black $(SRC)

	@echo "Running flake8..."
	cd server && flake8 $(SRC)

up:
	sudo docker compose up --build

down:
	sudo docker compose down

migrate:
	@echo "Applying migrations in alembic/versions..."
	alembic -c ./server/alembic.ini upgrade head

create_migration:
	alembic -c ./server/alembic.ini revision --autogenerate -m "$(args)"

run:
	./dev.sh

test:
	@echo "Running tests with pytest..."
	export $$(grep -v '^#' .env | xargs) && \
	pytest --cache-clear
