#!/bin/bash

git pull
chmod +x build.sh

docker image build -t revenberg/p1logger .

docker push revenberg/p1logger

# testing: 

echo "==========================================================="
echo "=                                                         ="
echo "=          docker run revenberg/p1logger                ="
echo "=                                                         ="
echo "==========================================================="
# docker run revenberg/p1logger