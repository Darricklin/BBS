#!/bin/bash

SCRIPT_DIR=`dirname $0`
cd $SCRIPT_DIR
PID=`cat ../gunicorn.pid`
kill $PID
cd -
