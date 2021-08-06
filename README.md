# DockerP1logger

sudo apt install gnupg2 pass
docker image build -t DockerP1logger  .
docker login -u revenberg
docker image push revenberg/DockerP1logger:latest

docker run revenberg/DockerP1logger

docker exec -it ??? /bin/sh

docker push revenberg/DockerP1logger: