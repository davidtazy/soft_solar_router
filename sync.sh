rsync --archive --verbose --perms   \
           --exclude 'venv' \
           --exclude '.git' \
           --exclude '__pycache__' \
           --exclude '.pytest_cache' \
           --exclude '.env' \
           --exclude '.vscode'   \
           --exclude '.env' \
           --exclude 'sync.sh' \
           . pi@192.168.1.38:/home/pi/soft_solar_router