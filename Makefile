deploy:
	docker-compose up --build -d
test:
	pytest . -k "not stages"
fmt:
	black -l 120 .
check:
	mypy .