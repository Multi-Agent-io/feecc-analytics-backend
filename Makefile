deploy:
	docker-compose up --build -d
test:
	pytest . -k "not stages"
