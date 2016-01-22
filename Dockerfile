FROM python:3.5-onbuild
MAINTAINER Jens Böttcher <eljenso.boettcher@gmail.com>

CMD [ "python", "./telegram-mopidy-bot.py" ]
