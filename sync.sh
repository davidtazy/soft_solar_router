set -ex
#rsync --archive --verbose --perms   \
rsync --archive  --perms   \
           --exclude 'venv' \
           --exclude '.git' \
           --exclude '__pycache__' \
           --exclude '.pytest_cache' \
           --exclude '.vscode'   \
           --exclude 'sync.sh' \
           --exclude 'sync_diff.sh' \
           --exclude 'soft_solar_router.log' \
           . david@home-server:~/soft_solar_router

