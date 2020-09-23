#!/usr/bin/env bash

# запускаем тесты в консоли
python -m unittest

# coverage
coverage run --source=bot, handlers, settings -m unittest
coverage report -m

# создаем bd PSQL
sudo -u postgres psql -c "create database vk_chat_bot"
sudo -u postgres psql -d vk_chat_bot

