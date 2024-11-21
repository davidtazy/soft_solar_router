#!/bin/bash

LOCAL_DIR="./"
REMOTE_DIR="/home/david/soft_solar_router/"
REMOTE_USER="david"
REMOTE_HOST="home-server"

file=soft_solar_router/switch/__main__.py

ssh "$REMOTE_USER@$REMOTE_HOST" "cat '$REMOTE_DIR$file'" | diff -u - "$LOCAL_DIR$file"