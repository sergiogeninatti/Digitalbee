# Project variables
DOCKER_COMPOSE_FILE = .docker/docker-compose.yml
DOCKER_COMPOSE = docker compose -f $(DOCKER_COMPOSE_FILE)
DOCKER_IMAGE = bot

# Default target is help
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show help with available commands
	@echo "Makefile commands:"
	@echo "build   - Build the docker image to run the project"
	@echo "up      - Start the telegram bot container using docker-compose (logs to stdout)"
	@echo "upd     - Start the telegram bot container using docker-compose in detached mode"
	@echo "logs    - Stream logs of the telegram bot container to stdout"
	@echo "shell   - Start a shell in the telegram bot docker container"
	@echo "stop    - Stop the telegram bot container"
	@echo "clean   - Remove all docker images for the project"

.PHONY: build
build: ## Build the docker image to run the project
	$(DOCKER_COMPOSE) build

.PHONY: up
up: ## Start the telegram bot container and stream logs to stdout
	$(DOCKER_COMPOSE) up

.PHONY: upd
upd: ## Start the telegram bot container in detached mode
	$(DOCKER_COMPOSE) up -d

.PHONY: logs
logs: ## Stream logs of the telegram bot container to stdout
	$(DOCKER_COMPOSE) logs -f

.PHONY: shell
shell: ## Start a shell in the telegram bot container
	$(DOCKER_COMPOSE) run  --rm $(DOCKER_IMAGE) /bin/bash

.PHONY: stop
stop: ## Stop the telegram bot container
	$(DOCKER_COMPOSE) down

.PHONY: clean
clean: ## Remove all docker images for the project
	docker rmi telegram-bot

# Makefile for managing Poetry dependencies

.PHONY: poetry-init pip-compile pip-update-and-compile

# Command to initialize Poetry and install required dependencies
poetry-init:
	@echo "Initializing Poetry and installing dependencies..."
	poetry install

# Command to compile dependencies into requirements.txt and requirements.dev.txt
pip-compile:
	@echo "Compiling dependencies..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --dev --output requirements.dev.txt --without-hashes

# Command to update all dependencies and compile the requirements
pip-update-and-compile:
	@echo "Updating dependencies..."
	poetry update
	@echo "Compiling updated dependencies..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --dev --output requirements.dev.txt --without-hashes
