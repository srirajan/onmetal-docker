
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
$ nova flavor-list |egrep 'Name|OnMetal'
| ID               | Name                    | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
| onmetal-compute1 | OnMetal Compute v1      | 32768     | 32   | 0         |      | 20    | 10000.0     | N/A       |
| onmetal-io1      | OnMetal IO v1           | 131072    | 32   | 3200      |      | 40    | 10000.0     | N/A       |
| onmetal-memory1  | OnMetal Memory v1       | 524288    | 32   | 0         |      | 24    | 10000.0     | N/A       |
```

 * Build our first Ubuntu 14.04 LTS (Trusty Tahr) On Metal server
```
key=sri-mb
nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name $key --poll play01
```

 * SSH to the server
```
nova ssh play01 --network=public
```

 * Poke around to review the hardware settings etc
```
less /proc/cpuinfo
free -g
ip addr
```

Prepare CoreOS cluster
======

* Before we do other stuff, let's spin up some core OS servers. First get a discovery URL for your cluster. More on this at https://coreos.com/docs/cluster-management/setup/cluster-discovery/

```
curl -w "\n" https://discovery.etcd.io/new
```

 * Edit the cloud init file named coreos-cluster/cloudinit.yaml. Replace the token url from above.


 * If you are doing on On Metal use coreos-cluster/cloudinit-onmetal.yaml as a workaround for https://github.com/coreos/coreos-cloudinit/issues/195. Eventually the above should work on both flavors.


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

Now let's play a litte with Docker.

 * Install docker on Ubuntu (play01 above)
```
apt-get update
apt-get install -y docker.io screen git vim
update-rc.d docker.io  defaults
```

 * Pull our first image. Review the listing & you should have 3 centos images for each of the versions.
```
docker pull centos
docker images
```

 * Run it. '-i' is for interactive & '-t' allocates a pseudo-tty. 
```
docker run -i -t centos /bin/bash
```

 * This runs the default image for CentOS. Review the inside to see how this looks inside docker.
```
cat /etc/redhat-release
ps
ls
whoami
cat /etc/hosts
exit
```

 * List Docker processes
```
docker ps -a
```

 * Run a different release
```
docker run -i -t centos:centos6 /bin/bash
cat /etc/redhat-release
exit
```

 * On the host(play01) with the networking. Docker uses a combination of Linux bridges and iptables to build managed networking on the container, communication with other containers and communication from the outside.

```
ifconfig docker0
iptables -nvL
iptables -nvL -t nat
```

 * Let's run something more than bash.
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

 * Let's do some more. Clone the repo from git
```
apt-get install -y git
git clone https://github.com/srirajan/onmetal-docker
```

 * Review the Dockerfile. This image file installs Nginx and PHP & loads a sample php file

```
cd /root/onmetal-docker/ubuntu_phpapp
cat Dockerfile
docker build -t="srirajan/ubuntu_phpapp" .
docker images
```

 *  Run the container and map the port 80 on the container to port 8082 on the host. You can curl the URL to see the site.

```
docker run -d -p 8082:80 "srirajan/ubuntu_phpapp"
docker top <container UID>
docker logs <container UID>
curl http://<IP>:8082/home.php
```

 * Docker diff
```
docker diff <container UID>
```

Now let's look at linking containers.


 * Start a mysql container and map the mysql port on the container to the host port 3306
```
docker run --name db -e MYSQL_ROOT_PASSWORD=dh47dk504dk44dd -d -p 3306:3306 mysql
docker logs db
```


 * Build the helper container
```
cd /root/onmetal-docker/dbhelper
docker build -t="srirajan/dbhelper" .
```

 * Start a helper container as a linked container and check it's environment variables. Linking allows information to be shared across containers. You can read more about linking here https://docs.docker.com/userguide/dockerlinks/ 
``` 
docker run --name dbhelper --link db:db srirajan/dbhelper env
```

 * Now if you run the actual container as it is, it will login to the mysql instance on the db container and install the world database.
```
docker rm dbhelper
docker run -d --name dbhelper --link db:db srirajan/dbhelper
docker logs dbhelper
```

 * For an even more complex example, let's try this. This Launches temporary IPython notebook servers and each instance runs on it's own containers. Note: This image is quite large and so can take long time to download.
```
export TOKEN=$( head -c 30 /dev/urandom | xxd -p )
docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=$TOKEN jupyter/configurable-http-proxy --default-target http://127.0.0.1:9999
docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=$TOKEN -v /var/run/docker.sock:/docker.sock  jupyter/tmpnb --docker-version="1.12" 
docker ps
```

 * Open a browser and access http://<server IP>:8000. Try opening a new notebook or a new terminal.


CoreOS, Fleet & Docker
=====

 * In the above steps, we should have created 4 core os machines with cloudinit. Now, lets play with CoreOS, etcd and Fleet. This should list all 4 machines in the cluster. Fleet is a distributed cluster management tool. It relies on etcd which is a distributed key value store for operation. It also works with systemd files and behaves like a distributed systemd in a multi-node setup.
```
fleetctl list-machines
```

 * Pull our repo on one of the nodes.
```
git clone https://github.com/srirajan/onmetal-docker
```

 * Review and load all the services. We wlll go into details of each service in following steps.
```
cd /home/core/onmetal-docker/fleet-services
fleetctl submit *.service
fleetctl list-unit-files
```

 * Run the db service.  This one is fairly simple service and runs a mysql container on one of the hosts. Wait for this service to start before proceeding.

```
fleetctl start db.service
fleetctl list-units
```

 * dbhelper.service uses container linking to install the mysql world database and configure some users for our application. The systemd configuration tells fleet to run on the same host as the db.service. mondb.service is not a container but uses systemd to run a script that updates etcd with the information about the db service. In this case we are just pushing private IPs to etcd but this can be leveraged to do other things as well.

```
fleetctl start dbhelper.service
fleetctl start mondb.service
```

 * Run fleetctl again to see where our containers are deployed. Because of our systemd definition file, fleet will ensure they run on the same host.
```
fleetctl list-units
```

 * You can also login to the host running the dbhelper service and review the journal(logs) for the service.
```
fleetctl journal dbhelper
```

 * Now let's move on the web container. Start the one container from the web service. In systemd a service with @ is generic service and you can append values to start as many of them.
```
fleetctl start web@01.service 
fleetctl list-units
```

 * Start 9 more web containers. Fleet will disribute them across the different hosts. 
```
fleetctl start web@{02..10}.service 
fleetctl list-units
```
 
 * Start the monweb services. These are similar to the mondb.service and update etcd with a different values from the running containers.
```
fleetctl start monweb@{01..10}.service 
fleetctl list-units
```


 * Query etcd for values. This will return the IP addresses and ports of the web containers. 
```
for i in {01..10}; do  etcdctl get /services/web/web$i/unit; etcdctl get /services/web/web$i/host; etcdctl get /services/web/web$i/public_ipv4_addr; etcdctl get /services/web/web$i/port; echo "-----" ; done
```

 * Test the site on one of the container.
```
curl http://<IP>:<Port>/home.php
```

 * At this point, we have database container running and a bunch of web containers running on different hosts. The communication between them has been established as well. 


 * Optionally, we can run the lbhelper service that updates the cloud load balancer. This requires a Rackspace cloud load balancer pre-configured and you need to set the values in etcd

```
etcdctl set /services/rscloud/OS_USERNAME <cloud username>
etcdctl set /services/rscloud/OS_REGION <cloud region>
etcdctl set /services/rscloud/OS_PASSWORD <cloud api key>
etcdctl set /services/rscloud/OS_TENANT_NAME <cloud account no>
etcdctl set /services/rscloud/LB_NAME <cloud lb name>
etcdctl set /services/rscloud/SERVER_HEALTH_URL health.php
etcdctl set /services/rscloud/SERVER_HEALTH_DIGEST dbe72348d4e3aa87958f421e4a9592a82839f3d8
```

 * Now run the lbhelper service. This will populate the load balancer with the IP addresses and port numbers from the web containers.
```
fleetctl start lbhelper.service 
```

What next?
======

 * Extend the db to be a cluster like mysql/galera.
 
 * Build a container that can be used to spin up additional core os hosts. You can also tie this to some form of load measurement or monitoring system.



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
