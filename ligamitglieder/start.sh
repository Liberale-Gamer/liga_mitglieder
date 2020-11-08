#!/bin/bash
cd $(dirname "$0")
source ./bin/activate
uwsgi --socket 0.0.0.0:7997 --protocol=http -w wsgi
