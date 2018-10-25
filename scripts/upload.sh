#!/bin/bash

LOCAL_DIR='./'
REMOTE_DIR='/project/bbs/'
USER='root'
HOST='35.194.171.19'

rsync -crvP --exclude={.git,.venv,__pycache__} $LOCAL_DIR $USER@$HOST:$REMOTE_DIR
