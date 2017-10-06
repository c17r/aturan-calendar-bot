#!/usr/bin/env bash

RUN=$PWD/local

LOGFILE=$RUN/aturan_calendar.log
CONFIGFILE=$RUN/secrets.json

pipenv run python -m src.aturan_calendar_bot -c $CONFIGFILE -l /$LOGFILE
