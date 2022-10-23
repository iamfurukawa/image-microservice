To build a new image:

docker build --tag=iamfurukawa/image-server:13 .
docker run --name image-server -p6662:6662 iamfurukawa/image-server:13

docker push iamfurukawa/image-server:13