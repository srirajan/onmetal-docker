

On Metal
======

 * List On Metal images
```
nova image-list |egrep 'Name|OnMetal'
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

Docker
======

Get running
=====

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

Simple examples
=====

 * Let's run something more
```
docker run -d  centos python -m SimpleHTTPServer 8888
```

 * And check a few things.
```
docker ps
docker top <container UID>
docker inspect <container UID> |less
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
docker run -d -p 8081:80 $dcont
docker logs <container UID>
```
 
 * Check the public IP for running Apache


* A little more evolved docker file. Install Nginx and PHP & load a sample file

```
cd /root/onmetal-docker/ubuntu_phpapp
cat Dockerfile
docker build -t="srirajan/ubuntu_phpapp" .
docker run -d -p 8082:80 "srirajan/ubuntu_phpapp"
docker top <container UID>
docker logs <container UID>
```

 * Docker diff
```
docker diff <container UID>
```

 * Docker port
```
docker port <container UID> 80
```

 * Push the file to the docker regitry
```
docker login
docker push "srirajan/ubuntu_phpapp"
```

Linking containers
=====
 * Start a mysql container
```
docker run --name db -e MYSQL_ROOT_PASSWORD=dh47dk504dk44dd -d -p 3306:3306 mysql
docker logs db
```

 * Build the helper container
```
cd /root/onmetal-docker/dbhelper
docker build -t="srirajan/dbhelper" .
```

 * Start a helper container and check it's environment
``` 
docker run --name dbhelper --link db:db srirajan/dbhelper env
```

 * Run a script to configure the DB
```
docker rm dbhelper
docker run --name dbhelper --link db:db srirajan/dbhelper /usr/local/bin/configuredb.sh
```

 * Create the web container
```
cd /root/onmetal-docker/web
docker build -t="srirajan/web" .
```

 * Run it
``` 
docker run --name web01 --link db:db  -p 8081:80 srirajan/web
```

 * Check URL http://<public IP>/world.php


CoreOS, Fleet & Docker
=====

 * Get a discovery URL. More on this at https://coreos.com/docs/cluster-management/setup/cluster-discovery/
```
curl -w "\n" https://discovery.etcd.io/new
```

 * Create a cloud init file and name it cloudinit.yaml. Replace the token url from above.
```
#cloud-config
coreos:
  etcd:
    # generate a new token for each unique cluster from https://discovery.etcd.io/new
    discovery: https://discovery.etcd.io/cb9fca019cc886363c3606a6e3b741e1
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001
  fleet:
    public-ip: $private_ipv4
  units:
    - name: etcd.service
      command: start
    - name: fleet.service
      command: start
      after: etcd.service

```

 * If you are doing on On Metal use this as a workaround for https://github.com/coreos/coreos-cloudinit/issues/195. Eventually the above should work. Save this file as cloudinit-onmetal.yaml

```
#cloud-config
coreos:
  etcd:
    # generate a new token for each unique cluster from https://discovery.etcd.io/new
    discovery: https://discovery.etcd.io/cb9fca019cc886363c3606a6e3b741e1
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001    
  fleet:
      public-ip: $private_ipv4
  units:
  - name: etcd.service
    command: start
    after: create-etcd-env.service
  - name: fleet.service
    command: start
    after: etcd.service
  - name: create-etcd-env.service
    command: start
    content: |
      [Unit]
      Description=creates etcd environment

      [Service]
      Before=etcd.service
      Type=oneshot
      ExecStart=/bin/sh -c "sed -i \"s/=:/=`ifconfig bond0.401 | grep 'inet ' | awk '{print $2}'`:/\" /run/systemd/system/etcd.service.d/20-cloudinit.conf && systemctl daemon-reload && systemctl etcd restart"
```

 * Decide which flavor you are using

```
#On metal
flavor=onmetal-compute1
image=75a86b9d-e016-4cb7-8532-9e9b9b5fc58b
key=sri-mb
cloudinit=cloudinit-onmetal.yaml

# Performance 
flavor=performance1-1
image=749dc22a-9563-4628-b0d1-f84ced8c7b7a
key=sri-mb
cloudinit=cloudinit.yaml
```

 * Boot 4 servers for the cluster
```
nova boot --flavor $flavor --image $image  --key-name $key --config-drive true --user-data $cloudinit core01
nova boot --flavor $flavor --image $image  --key-name $key --config-drive true --user-data $cloudinit core02
nova boot --flavor $flavor --image $image  --key-name $key --config-drive true --user-data $cloudinit core03
nova boot --flavor $flavor --image $image  --key-name $key --config-drive true --user-data $cloudinit core04
```


 * Now, lets play with Fleet. List machines.
```
fleetctl list-machines
```

 * Create a systemd file for Fleet. Name this 'web@.service'.  The naming convention is quite important & it allows you to have a single configuration and easily create new units.
```
[Unit]
Description=Web
After=docker.service
Requires=docker.service
 
[Service]
EnvironmentFile=/etc/environment
TimeoutStartSec=0
ExecStartPre=/usr/bin/docker pull srirajan/ubuntu_phpapp
ExecStart=/usr/bin/docker run --rm --name web-%i -p ${COREOS_PUBLIC_IPV4}:808%i:80 srirajan/ubuntu_phpapp
ExecStop=/usr/bin/docker stop web-%i
Restart=always

[X-Fleet]
Conflicts=web@*.service
```

 * Submit this service to fleet
```
fleetctl submit web\@.service 
fleetctl list-unit-files
```

 * Start the service
```
fleetctl start web@1.service 
fleetctl list-units
```

 * Start more
```
fleetctl start web@{2..4}.service 
fleetctl list-units
```
 
 * Do some playing
```
fleetctl journal web@1.service
docker ps
```

 * Create a watch/sidekick service
```
[Unit]
Description=Monitors web services
Requires=etcd.service
Requires=web@%i.service
BindsTo=web@%i.service

[Service]
EnvironmentFile=/etc/environment

ExecStart=/bin/bash -c '\
  while true; do \
    curl -f ${COREOS_PUBLIC_IPV4}:808%i; \
    if [ $? -eq 0 ]; then \
      etcdctl set /services/web/web%i \'{"unit": "%n","host": "%H", "public_ipv4_addr": ${COREOS_PUBLIC_IPV4}, "private_ipv4_addr": ${COREOS_PRIVATE_IPV4},  "port": 808%i}\' --ttl 10; \
    else \
      etcdctl rm /services/web/${COREOS_PUBLIC_IPV4}; \
    fi; \
    sleep 10; \
  done'

# Stop
ExecStop=/usr/bin/etcdctl rm /services/apache/${COREOS_PUBLIC_IPV4}

[X-Fleet]
# Schedule on the same machine as the associated Apache service
X-ConditionMachineOf=web@%i.service
```

 * Start services
```
fleetctl start monweb@{1..4}.service 
```

 * Query etcd
```
for i in {1..4}; do etcdctl get /services/web/web$i; done
```


Misc Commands
======

 * etcd logs
```
journalctl -u etcd
```

 * Delete all containers
```
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
```

 * Delete all images
```
docker rmi $(docker images -q)
```


Credits
======
 * Simone Soldateschi - https://github.com/siso
