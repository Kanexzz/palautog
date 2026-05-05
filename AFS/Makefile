.PHONY: help install migrate run test clean docker-up docker-down

help:
	@echo "Faculty Scheduling System - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies"
	@echo "  make migrate          - Run database migrations"
	@echo "  make seed             - Create demo data"
	@echo ""
	@echo "Development:"
	@echo "  make run              - Start development server"
	@echo "  make test             - Run tests"
	@echo "  make shell            - Django shell"
	@echo ""
	@echo "Database:"
	@echo "  make reset-db         - Reset database (WARNING: deletes data)"
	@echo "  make createsuperuser  - Create admin user"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Clean cache and temp files"
	@echo "  make lint             - Run code linting"
	@echo ""

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

seed:
	python manage.py create_demo_data

run:
	python manage.py runserver

test:
	python manage.py test

shell:
	python manage.py shell

reset-db:
	rm -f db.sqlite3
	python manage.py migrate
	python manage.py create_demo_data

createsuperuser:
	python manage.py createsuperuser

docker-up:
	docker-compose up -d
	@echo "Services started. Access at http://localhost:8000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/

lint:
	flake8 apps/ config/

freeze:
	pip freeze > requirements_frozen.txt

static:
	python manage.py collectstatic --noinput

gunicorn:
	gunicorn config.wsgi:application --bind 0.0.0.0:8000
