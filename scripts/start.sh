#!/bin/bash

CURRENT_DIR=`pwd`
SCRIPT_DIR=`dirname $0`
cd $SCRIPT_DIR
cd ..
source .venv/bin/activate
gunicorn -c bbs/gunicorn-config.py bbs.wsgi
cd $CURRENT_DIR
