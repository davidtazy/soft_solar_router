set -ex

rsync --archive --verbose --perms   \
           --exclude 'venv' \
           --exclude '.git' \
           --exclude '__pycache__' \
           --exclude '.pytest_cache' \
           --exclude '.vscode'   \
           --exclude 'sync.sh' \
           --exclude 'soft_solar_router.log' \
           . david@192.168.1.47:~/soft_solar_router

