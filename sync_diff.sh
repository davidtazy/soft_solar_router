set -ex
#rsync --archive --verbose --perms   \
rsync -avun --delete   \
           --exclude 'venv' \
           --exclude '.git' \
           --exclude '__pycache__' \
           --exclude '.pytest_cache' \
           --exclude '.vscode'   \
           --exclude 'sync.sh' \
           --exclude 'soft_solar_router.log' \
           . david@home-server:~/soft_solar_router

