#!/bin/bash

# version 7-8-2021

cd ~/dockerp1logger
rc=$(git remote show origin |  grep "local out of date" | wc -l)

if [ $rc -ne "0" ]; then
    git pull
    chmod +x build.sh

    docker image build -t revenberg/p1logger .

    docker push revenberg/p1logger

    # testing: 

    echo "==========================================================="
    echo "=                                                         ="
    echo "=          docker run revenberg/p1logger                  ="
    echo "=                                                         ="
    echo "==========================================================="
    # docker run revenberg/p1logger
fi