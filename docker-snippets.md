
Docker install
======

 * Basic setup
```
apt-get update
apt-get upgrade
update-rc.d docker.io  defaults
docker pull ubuntu
docker pull centos
```


Docker commands
======

 * Common tasks
 
```
docker images
docker top
docker ps
docker logs
docker inspect -f '{{ .NetworkSettings.IPAddress }}' 6fef2717447c
```

 * Run bash
```
docker run -i -t ubuntu /bin/bash
```

 * Delete all containers
```
docker rm $(docker ps -a -q)
```

 * Delete all images
```
docker rmi $(docker images -q)
```


OnMetal Builds
======

 * Boot onmetal ubuntu 14.04

```
nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name sri-mb metal01 --meta onwner=sri
```

 * Core os
```
nova boot --flavor onmetal-compute1 --image 85e3d8d2-6d0f-4ded-bd55-0f13d3e57e69 --key-name sri-mb metal02 --meta onwner=sri
```

Docker builds
======

 * Run bash
```
docker run -i -t ubuntu /bin/bash
```

 * Simple apache

```
cd /root
git clone https://github.com/srirajan/onmetal-docker
dcont=ubuntu_apache
cd /root/onmetal-docker/$dcont
docker build -t="$dcont" .
docker run -d -p 8081:80 $cont
```

 * Nginx and PHP

```
dcont=ubuntu_phpapp
cd /root/onmetal-docker/$dcont
docker build -t="$dcont" .
docker run -d -p 8082:80 $cont
```


