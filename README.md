# dockerp1logger

sudo apt install gnupg2 pass
docker image build -t dockerp1logger  .
docker login -u revenberg
docker image push revenberg/dockerp1logger:latest

docker run revenberg/dockerp1logger

docker exec -it ??? /bin/sh

docker push revenberg/dockerp1logger: