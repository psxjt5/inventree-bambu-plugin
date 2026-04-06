#!/bin/bash

set -e  # Exit on error

CONTAINER="inventree-server"

echo "Updating plugins inside container: $CONTAINER"

# Run everything inside the container
docker exec -i $CONTAINER bash << 'EOF'

set -e

PLUGIN1_DIR="/home/inventree/data/inventree-3d-printing"
PLUGIN2_DIR="/home/inventree/data/inventree-bambu-plugin"
STATIC_DIR="/home/inventree/data/static/plugins/inventree_bambu"

echo "Pulling latest code..."

cd $PLUGIN1_DIR
git pull

cd $PLUGIN2_DIR
git pull

echo "Copying frontend assets..."

rm -rf $STATIC_DIR/*
cp -r $PLUGIN2_DIR/inventree_bambu/static/* $STATIC_DIR/

echo "Plugin update complete"

EOF

echo "Restarting container..."
docker restart $CONTAINER

echo "Done!"