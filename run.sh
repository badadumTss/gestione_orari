#!/bin/sh

wget "https://calendar.google.com/calendar/ical/c_ms9a6ag26gub7qaalplfeb4li8%40group.calendar.google.com/public/basic.ics" -O impegni.ics 2> wget.log
./main.py orari.json impegni.ics
