#!/bin/bash

git pull
chmod +x build.sh

docker image build -t revenberg/DockerP1logger .

docker push revenberg/DockerP1logger

# testing: 

echo "==========================================================="
echo "=                                                         ="
echo "=          docker run revenberg/DockerP1logger                ="
echo "=                                                         ="
echo "==========================================================="
# docker run revenberg/DockerP1logger