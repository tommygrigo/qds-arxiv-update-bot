# arXiv update bot


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)]("https://github.com/psf/black)
[![GitHub release](https://img.shields.io/github/release/nanoy42/arxiv-update-bot.svg)](https://github.com/nanoy42/arxiv-update-bot/releases/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Docker](https://img.shields.io/docker/v/nanoy/arxiv-update-bot?label=Docker)](https://hub.docker.com/r/nanoy/arxiv-update-bot)

arxiv update bot is a simple python script that scraps the arXiv, search for interesting paper and send a message on telegram if any was found.

## Note:

This repository is Tommaso Grigoletto's personal fork of the great [arxiv update bot](https://github.com/nanoy42/arxiv-update-bot). All the credit for the code goes to [nanoy42](https://github.com/nanoy42). 

I simply adapted the code to include the search for favorite authors and some changes in order to run the bot entirely on Github using Github actions and secrets. 