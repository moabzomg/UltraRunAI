.PHONY: build up down restart logs scrape

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down && docker-compose up -d

logs:
	docker-compose logs -f

scrape-runner:
	docker-compose run scraper python3 runner_scraper.py data/cleaned_runner_ids.json

scrape-race:
	docker-compose run scraper python3 race_scraper.py

scrape-all:
	docker-compose run scraper ./scrape_all_runners.sh

scrape-clean:
	docker-compose run scraper python3 clean.py