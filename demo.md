
This exercise will review Rackspace On Metal, an intro to Docker, review of CoreOS & Fleet and demonstrate how one could use all of them to build a multi-tier application. 

The associated presentation on this can be found at TODO:slide share link

Before you start
======

You will need the following
 
 * A Rackspace cloud account. Get a free  tier Rackspace developer account - https://developer.rackspace.com/signup/
 
 * If you don't have an account, you can still follow this and do it on your own servers.  Some of the examples are specific to Rackspace cloud servers but the ones around Docker, CoreOS and Fleet can be done on any server.

 * For any questions, just raise an issue in Git.

 * Ensure you have novaclient installed. Refer to http://www.rackspace.com/knowledge_center/article/installing-python-novaclient-on-linux-and-mac-os for more details.


On Metal
======
 
As of Nov, 2014, On Metal is only available in US region of IAD. So you need a Rackspace US cloud account. You can read more about On Metal here. http://www.rackspace.com/cloud/servers/onmetal/

 * List all On Metal images
```
$ nova image-list |egrep 'Name|OnMetal'
| ID                                   | Name                                                                                         | Status | Server                               |
| e9f4497a-2ec2-471c-ad1c-f491786a44d9 | OnMetal - CentOS 6.5                                                                         | ACTIVE |                                      |
| 6d7d1f79-dbff-4cdc-a71c-0f7ad4ea9c3a | OnMetal - CentOS 7                                                                           | ACTIVE |                                      |
| ef2ab1c3-8ab6-477d-a38e-8225b071ffc3 | OnMetal - CoreOS (Alpha)                                                                     | ACTIVE |                                      |
| 43a4650f-a45b-4bcf-abbb-bb1c8dc9a50f | OnMetal - CoreOS (Beta)                                                                      | ACTIVE |                                      |
| 75a86b9d-e016-4cb7-8532-9e9b9b5fc58b | OnMetal - CoreOS (Stable)                                                                    | ACTIVE |                                      |
| c7cb5085-27e5-4f18-a065-7759ae2aba3a | OnMetal - Debian 7 (Wheezy)                                                                  | ACTIVE |                                      |
| 43415443-ecb7-4419-870c-98201addfded | OnMetal - Debian Testing (Jessie)                                                            | ACTIVE |                                      |
| b6713711-5ddf-44fb-b31b-32e9a691a73d | OnMetal - Debian Unstable (Sid)                                                              | ACTIVE |                                      |
| 7c5fdb31-a853-4786-a84a-03b45fb14bbd | OnMetal - Fedora 20 (Heisenbug)                                                              | ACTIVE |                                      |
| 4b960e01-897b-46d8-a81c-20729d28485c | OnMetal - Ubuntu 12.04 LTS (Precise Pangolin)                                                | ACTIVE |                                      |
| 06bb130b-7607-46f9-85ae-124bae4d0f5b | OnMetal - Ubuntu 14.04 LTS (Trusty Tahr)                                                     | ACTIVE |                                      |
```

 * List On Metal flavors
```
nova flavor-list |egrep 'Name|OnMetal'
```

 * Build a Ubuntu 14.04 LTS (Trusty Tahr) On Metal server
```
key=sri-mb
nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name $key --poll play01
```

 * SSH to the server
```
nova ssh play01 --network=public
```

 * Poke around
```
less /proc/cpuinfo
free -g
ip addr
```

Prepare CoreOS cluster
======

* Before we do other stuff, let's spin up some core OS servers. First get a discovery URL. More on this at https://coreos.com/docs/cluster-management/setup/cluster-discovery/
```
curl -w "\n" https://discovery.etcd.io/new
```

 * Edit the cloud init file named cloudinit.yaml. Replace the token url from above.


 * If you are doing on On Metal use cloudinit-onmetal.yaml as a workaround for https://github.com/coreos/coreos-cloudinit/issues/195. Eventually the above should work. 


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


Docker
======

 * Install docker on Ubuntu (play01 above)
```
apt-get update
apt-get install -y docker.io screen git vim
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
docker ps -a
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
```

 * The docker file. Install Nginx and PHP & load a sample file

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
docker run -d --name dbhelper --link db:db srirajan/dbhelper
docker logs dbhelper
```



CoreOS, Fleet & Docker
=====

 * In the above steps, we should have created 4 core os machines with cloudinit. Now, lets play with CoreOS, etcd and Fleet.
```
fleetctl list-machines
```

 * Pull our repo
```
git clone https://github.com/srirajan/onmetal-docker
```


 * Review and load the db services
```
cd /home/core/onmetal-docker/fleet-services
fleetctl submit *.service
fleetctl list-unit-files
```

 * Run them
```
fleetctl start db.service
fleetctl start dbhelper.service
fleetctl start mondb.service
fleetctl list-units
```

 * Start the one container from the web service
```
fleetctl start web@01.service 
fleetctl list-units
```

 * Start more
```
fleetctl start web@{02..10}.service 
fleetctl list-units
```
 
 * Start the monweb services
```
fleetctl start monweb@{01..10}.service 
```
fleetctl destroy monweb@{01..10}.service 


 * Query etcd for values
```
for i in {01..10}; do etcdctl get /services/web/web$i/host; done
for i in {01..10}; do etcdctl get /services/web/web$i/public_ipv4_addr; etcdctl get /services/web/web$i/port; done
```

 * Test the site
```
curl http://<IP>:<Port>/home.php
```

 * Optionally, run the lbhelper service that updates the load balancer. This requires a Rackspace cloud load balancer pre-configured.  First set the values in etcd

```
etcdctl set /services/rscloud/OS_USERNAME <cloud username>
etcdctl set /services/rscloud/OS_REGION <cloud region>
etcdctl set /services/rscloud/OS_PASSWORD <cloud api key>
etcdctl set /services/rscloud/OS_TENANT_NAME <cloud account no>
etcdctl set /services/rscloud/LB_NAME <cloud lb name>
etcdctl set /services/rscloud/SERVER_HEALTH_URL health.php
etcdctl set /services/rscloud/SERVER_HEALTH_DIGEST dbe72348d4e3aa87958f421e4a9592a82839f3d8
```

 * Run the lbhelper service
```
fleetctl start lbhelper.service 
```


Misc Commands
======

 * Review logs of etcd and fleet
```
journalctl -u etcd
journalctl -u fleet
```

 * Delete all containers
```
docker stop $(docker ps -a -q)
sleep 2
docker rm $(docker ps -a -q)
```

 * Delete all images
```
docker rmi $(docker images -q)
```

 * Cleanup fleet
```
fleetctl destroy $(fleetctl list-units -fields=unit -no-legend)
fleetctl destroy $(fleetctl list-unit-files -fields=unit -no-legend)
sleep 5
fleetctl list-unit-files
fleetctl list-units
```

 * restart Fleet
```
sudo systemctl restart fleet.service
```

Resources
======

 * Free Rackspace developer account - https://developer.rackspace.com/signup/

 * Core OS - https://coreos.com/docs/


Credits
======
 * Simone Soldateschi - https://github.com/siso
 * Kyle Kelley - https://github.com/rgbkrk
 * tmpnb - https://github.com/jupyter/tmpnb
