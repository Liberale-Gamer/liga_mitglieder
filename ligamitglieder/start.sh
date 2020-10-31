#!/bin/bash
cd /home/liga_mitglieder/ligamitglieder
source ./bin/activate
uwsgi --socket 0.0.0.0:7997 --protocol=http -w wsgi
