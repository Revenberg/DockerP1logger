# p1logger

sudo apt install gnupg2 pass
docker image build -t p1logger  .
docker login -u revenberg
docker image push revenberg/p1logger:latest

docker run revenberg/p1logger

docker exec -it ??? /bin/sh

docker push revenberg/p1logger: