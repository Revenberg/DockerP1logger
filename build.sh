#!/bin/bash

git pull
chmod +x build.sh

docker image build -t revenberg/dockerp1logger .

docker push revenberg/dockerp1logger

# testing: 

echo "==========================================================="
echo "=                                                         ="
echo "=          docker run revenberg/dockerp1logger                ="
echo "=                                                         ="
echo "==========================================================="
# docker run revenberg/dockerp1logger