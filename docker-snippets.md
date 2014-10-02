

# Delete all containers
```
docker rm $(docker ps -a -q)
```

# Delete all images
```
docker rmi $(docker images -q)
```


Boot onmetal ubuntu 14.04

```
nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name sri-mb metal01 --meta onwner=sri
```

Docker install

```
apt-get update
apt-get upgrade
update-rc.d docker.io  defaults
docker pull ubuntu
docker pull centos
```

Docker cmd

```
docker images
docker top
docker ps
docker logs
docker inspect -f '{{ .NetworkSettings.IPAddress }}' 6fef2717447c
```


core os
```
nova boot --flavor onmetal-compute1 --image 85e3d8d2-6d0f-4ded-bd55-0f13d3e57e69 --key-name sri-mb metal02 --meta onwner=sri
```



