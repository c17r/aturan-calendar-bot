#!/usr/bin/env bash

RUN=$PWD/run
CURRENT=$RUN/current

LOGFILE=$RUN/aturan_calendar.log
CONFIGFILE=$RUN/secrets.json

source $CURRENT/venv/bin/activate

aturan_calendar_bot -c $CONFIGFILE >> /$LOGFILE
