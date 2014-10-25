

 * List On Metal images
```
nova image-list |egrep 'Name|OnMetal; 
```

 * List On Metal images
```
nova flavor-list |egrep 'Name|OnMetal'
```

 * Build a Ubuntu 14.04 LTS (Trusty Tahr) On Metal server
```
date; nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name sri-mb play01 --progress; date
```

 * Login to the server
```
nova ssh play01 --network=public
```

 * Look around
```
less /proc/cpuinfo
free -g
ip addr
```

 * Install docker on Ubuntu
```
apt-get update
apt-get install docker.io
update-rc.d docker.io  defaults
```

 * Our first image
```
docker pull centos
docker images
```

 * Run it. '-i' is for interactive & '-t' allocates a pseudo-tty. 
```
docker run -i -t centos /bin/bash
```

 * This runs the default image for CentOS. Play with it
```
cat /etc/redhat-release
ps
ls
whoami
cat /etc/hosts
exit
```

 * Run a different release
```
docker run -i -t centos:centos6 /bin/bash
```

 * A brief look at the host networking
```
ifconfig docker0
iptables -nvL
iptables -nvL -t nat
```

 * Let's run something more
```
docker run -d  centos python -m SimpleHTTPServer 8888
```

 * And check a few things.
```
docker ps
docker top <container UID>
docker inspect <container UID> |less
docker inspect -f '{{ .NetworkSettings.IPAddress }}' <container UID>
curl  http://<container IP>:8888
```

 * Let's do some more 
```
apt-get install -y git
git clone https://github.com/srirajan/onmetal-docker
docker pull ubuntu
```

 * The docker file
```
dcont=ubuntu_apache
cd /root/onmetal-docker/$dcont
less Dockerfile
```

 * Build it
```
docker build -t="$dcont" .
docker run -d -p 8080:80 $dcont
docker logs <container UID>
```
 
 * Check the public IP for running Apache


* A little more envolved docker file. Nginx and PHP

```
dcont=ubuntu_phpapp
cd /root/onmetal-docker/$dcont
less Dockerfile
docker build -t="$dcont" .
docker run -d -p 8082:80 $cont
```



