
This exercise will review Rackspace On Metal, an intro to Docker, review of CoreOS & Fleet and demonstrate how one could use all of them to build a multi-tier application. 

The associated presentation on this can be found at bit.ly/rs-onmetal-docker

Before you start
======

You will need the following
 
 * A Rackspace cloud account. Get a free tier Rackspace developer account - https://developer.rackspace.com/signup/
 
 * If you don't have an account, you can still follow this and do it on your own servers.  Some of the examples are specific to Rackspace cloud servers but the ones around Docker, CoreOS and Fleet can be done on any server.

 * For any questions, just raise an issue in Git.

 * Ensure you have novaclient installed. Refer to http://www.rackspace.com/knowledge_center/article/installing-python-novaclient-on-linux-and-mac-os for more details.


On Metal
======
 
As of Nov, 2014, On Metal is only available in US region of IAD. So you need a Rackspace US cloud account. You can read more about On Metal here. http://www.rackspace.com/cloud/servers/onmetal/

 * Build our first Ubuntu 14.04 LTS (Trusty Tahr) On Metal server
```
key=sri-mb
nova boot --flavor onmetal-compute1 \
--image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a \
--key-name $key \
--poll play01
```

 * While that is building, let's look around. List all On Metal images
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

 * Once the server has finished building SSH to the server
```
nova ssh play01 --network=public
```

 * Poke around to review the hardware settings etc
```
less /proc/cpuinfo
free -g
ip addr
lshw
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
nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core01

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core02

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core03

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core04
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

 * On the host (play01) with the networking. Docker uses a combination of Linux bridges and iptables to build managed networking on the container, communication with other containers and communication from the outside.

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
docker inspect <container UID>

#curl the container IP
curl http://<container IP>/home.php

#curl the public IP and port
curl http://<IP>:8082/home.php
```

 * Docker diff
```
docker diff <container UID>
```

 * Now let's look at linking containers. Start a mysql container and map the mysql port on the container to the host port 3306
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

docker run -d --name dbhelper --link db:db srirajan/dbhelper  /usr/local/bin/configuredb.sh

docker logs dbhelper
```

 * For an even more complex example, let's try this. This Launches temporary IPython notebook servers and each instance runs on it's own containers. Note: This image is quite large and so can take long time to download.
```
docker pull jupyter/demo

export TOKEN=$( head -c 30 /dev/urandom | xxd -p )

docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=$TOKEN jupyter/configurable-http-proxy \
--default-target http://127.0.0.1:9999

docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=$TOKEN -v /var/run/docker.sock:/docker.sock \
jupyter/tmpnb python orchestrate.py --cull-timeout=60 --docker-version="1.12" \
--command="ipython3 notebook --NotebookApp.base_url={base_path} --ip=0.0.0.0 --port {port}"

docker ps
```

 * Open a browser and access http://<server IP>:8000. Try opening a new notebook or a new terminal.


CoreOS, Fleet & Docker
=====

 * In the above steps, we should have created 4 core os machines with cloudinit. Now, lets play with CoreOS, etcd and Fleet. This should list all 4 machines in the cluster. Fleet is a distributed cluster management tool. It relies on etcd, which is a distributed key value store for operation. It also works with systemd files and behaves like a distributed systemd in a multi-node setup.
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
```

```
fleetctl list-unit-files
UNIT			    HASH	DSTATE		STATE		TARGET
db.service		    fbf415a	launched	launched	-
dbhelper.service	747c778	inactive	inactive	-
lbhelper.service	0592528	inactive	inactive	-
mondb.service		a4f50cc	inactive	inactive	-
monweb@.service		d5ed242	inactive	inactive	-
web@.service		0ac8be5	inactive	inactive	-
```

 * Run the db service.  

```
fleetctl start db.service
Unit db.service launched on 2aa4e35a.../10.208.201.253

fleetctl list-units
UNIT		MACHINE				ACTIVE	SUB
db.service	2aa4e35a.../10.208.201.253	active	running
```

 * You can also review the systemd service file. This one is fairly simple service and runs a mysql container on one of the hosts. Wait for this service to start before proceeding. Also note, that Fleet decides which host to run the container on.
```
cat db.service 
[Unit]
Description=DB service
Requires=etcd.service

[Service]
EnvironmentFile=/etc/environment
TimeoutStartSec=0
ExecStartPre=/usr/bin/docker pull mysql
ExecStart=/usr/bin/docker run --rm --name db -e MYSQL_ROOT_PASSWORD=dh47dk504dk44dd -p ${COREOS_PRIVATE_IPV4}:3306:3306 mysql
ExecStop=/usr/bin/docker stop db
Restart=always

```

 * One oddity with fleet is that to query the status, you have to run the command on the host running the container.
```
fleetctl status db.service
db.service - DB service
   Loaded: loaded (/run/fleet/units/db.service; linked-runtime)
   Active: active (running) since Thu 2014-11-13 14:11:06 UTC; 8min ago
  Process: 22050 ExecStartPre=/usr/bin/docker pull mysql (code=exited, status=0/SUCCESS)
 Main PID: 22068 (docker)
   CGroup: /system.slice/db.service
           └─22068 /usr/bin/docker run --rm --name db -e MYSQL_ROOT_PASSWORD=dh47dk504dk44dd -p 10.208.201.253:3306:3306 mysql

Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Warning] No existing UUID has been found, so we assume that this is the first time that this server has been started. Generating a new UUID: ec53a4d8-6b3e-11e4-8386-0a1bbbebe238.
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] Server hostname (bind-address): '*'; port: 3306
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] IPv6 is available.
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note]   - '::' resolves to '::';
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] Server socket created on IP: '::'.
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] Event Scheduler: Loaded 0 events
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] Execution of init_file '/tmp/mysql-first-time.sql' started.
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] Execution of init_file '/tmp/mysql-first-time.sql' ended.
Nov 13 14:11:12 core04 docker[22068]: 2014-11-13 14:11:12 1 [Note] mysqld: ready for connections.
Nov 13 14:11:12 core04 docker[22068]: Version: '5.6.21'  socket: '/tmp/mysql.sock'  port: 3306  MySQL Community Server (GPL)
```


 * dbhelper.service uses container linking to install the mysql world database and configure some users for our application. The systemd configuration tells fleet to run on the same host as the db.service. mondb.service is not a container but uses systemd to run a script that updates etcd with the information about the db service. In this case we are just pushing private IPs to etcd but this can be leveraged to do other things as well.

```
fleetctl start dbhelper.service
Unit dbhelper.service launched on 2aa4e35a.../10.208.201.253

fleetctl start mondb.service
Unit mondb.service launched on 2aa4e35a.../10.208.201.253

```

 * Run fleetctl again to see where our containers are deployed. Because of our systemd definition file, fleet will ensure they run on the same host.
```
fleetctl list-units
UNIT			MACHINE				ACTIVE	SUB
db.service		2aa4e35a.../10.208.201.253	active	running
dbhelper.service	2aa4e35a.../10.208.201.253	active	running
mondb.service		2aa4e35a.../10.208.201.253	active	running
```

 * You can also login to the host running the dbhelper service and review the journal (logs) for the service.
```
fleetctl journal dbhelper
-- Logs begin at Mon 2014-11-10 21:00:41 UTC, end at Thu 2014-11-13 14:23:43 UTC. --
Nov 11 05:22:51 core04.novalocal systemd[1]: Stopped DB Helperservice.
Nov 11 05:22:51 core04.novalocal systemd[1]: Unit dbhelper.service entered failed state.
-- Reboot --
Nov 13 14:22:43 core04 systemd[1]: Starting DB Helperservice...
Nov 13 14:22:43 core04 docker[22239]: Pulling repository srirajan/dbhelper
Nov 13 14:23:00 core04 systemd[1]: Started DB Helperservice.
Nov 13 14:23:06 core04 docker[22272]: Creating the world database
Nov 13 14:23:13 core04 docker[22272]: Creating application user
Nov 13 14:23:13 core04 docker[22272]: Counting rows in world.city
Nov 13 14:23:13 core04 docker[22272]: COUNT(*)
Nov 13 14:23:13 core04 docker[22272]: 4079
```

 * Now let's move on the web containers. Start the one container from the web service. In systemd a service with @ is generic service and you can append values to start as many of them. The first container will take a little bit of time as it is downloading the container.
```
fleetctl start web@01.service 
Unit web@01.service launched on 6847f4f7.../10.208.201.226

fleetctl list-units
UNIT			MACHINE				ACTIVE		SUB
db.service		2aa4e35a.../10.208.201.253	active		running
dbhelper.service	2aa4e35a.../10.208.201.253	active		running
mondb.service		2aa4e35a.../10.208.201.253	active		running
web@01.service		6847f4f7.../10.208.201.226	active	running
```

 * Start 9 more web containers. Fleet will disribute them across the different hosts. 
```
fleetctl start web@{02..10}.service 
Unit web@04.service launched on ee5398cf.../10.208.201.250
Unit web@10.service launched on 2aa4e35a.../10.208.201.253
Unit web@07.service launched on 6847f4f7.../10.208.201.226
Unit web@09.service launched on ee5398cf.../10.208.201.250
Unit web@03.service launched on 6847f4f7.../10.208.201.226
Unit web@05.service launched on c3f52cb3.../10.208.201.234
Unit web@02.service launched on ee5398cf.../10.208.201.250
Unit web@06.service launched on c3f52cb3.../10.208.201.234
Unit web@08.service launched on c3f52cb3.../10.208.201.234

fleetctl list-units
UNIT			MACHINE				ACTIVE	SUB
db.service		2aa4e35a.../10.208.201.253	active	running
dbhelper.service	2aa4e35a.../10.208.201.253	active	running
mondb.service		2aa4e35a.../10.208.201.253	active	running
web@01.service		6847f4f7.../10.208.201.226	active	running
web@02.service		ee5398cf.../10.208.201.250	active	running
web@03.service		6847f4f7.../10.208.201.226	active	running
web@04.service		ee5398cf.../10.208.201.250	active	running
web@05.service		c3f52cb3.../10.208.201.234	active	running
web@06.service		c3f52cb3.../10.208.201.234	active	running
web@07.service		6847f4f7.../10.208.201.226	active	running
web@08.service		c3f52cb3.../10.208.201.234	active	running
web@09.service		ee5398cf.../10.208.201.250	active	running
web@10.service		2aa4e35a.../10.208.201.253	active	running
```
 
 * Start the monweb services. These are similar to the mondb.service and update etcd with different values from the running containers.
```
fleetctl start monweb@{01..10}.service 
Unit monweb@04.service launched on ee5398cf.../10.208.201.250
Unit monweb@02.service launched on ee5398cf.../10.208.201.250
Unit monweb@01.service launched on 6847f4f7.../10.208.201.226
Unit monweb@05.service launched on c3f52cb3.../10.208.201.234
Unit monweb@03.service launched on 6847f4f7.../10.208.201.226
Unit monweb@09.service launched on ee5398cf.../10.208.201.250
Unit monweb@07.service launched on 6847f4f7.../10.208.201.226
Unit monweb@10.service launched on 2aa4e35a.../10.208.201.253
Unit monweb@08.service launched on c3f52cb3.../10.208.201.234
Unit monweb@06.service launched on c3f52cb3.../10.208.201.234

fleetctl list-units
UNIT			MACHINE				ACTIVE	SUB
db.service		2aa4e35a.../10.208.201.253	active	running
dbhelper.service	2aa4e35a.../10.208.201.253	active	running
mondb.service		2aa4e35a.../10.208.201.253	active	running
monweb@01.service	6847f4f7.../10.208.201.226	active	running
monweb@02.service	ee5398cf.../10.208.201.250	active	running
monweb@03.service	6847f4f7.../10.208.201.226	active	running
monweb@04.service	ee5398cf.../10.208.201.250	active	running
monweb@05.service	c3f52cb3.../10.208.201.234	active	running
monweb@06.service	c3f52cb3.../10.208.201.234	active	running
monweb@07.service	6847f4f7.../10.208.201.226	active	running
monweb@08.service	c3f52cb3.../10.208.201.234	active	running
monweb@09.service	ee5398cf.../10.208.201.250	active	running
monweb@10.service	2aa4e35a.../10.208.201.253	active	running
web@01.service		6847f4f7.../10.208.201.226	active	running
web@02.service		ee5398cf.../10.208.201.250	active	running
web@03.service		6847f4f7.../10.208.201.226	active	running
web@04.service		ee5398cf.../10.208.201.250	active	running
web@05.service		c3f52cb3.../10.208.201.234	active	running
web@06.service		c3f52cb3.../10.208.201.234	active	running
web@07.service		6847f4f7.../10.208.201.226	active	running
web@08.service		c3f52cb3.../10.208.201.234	active	running
web@09.service		ee5398cf.../10.208.201.250	active	running
web@10.service		2aa4e35a.../10.208.201.253	active	running
```


 * Query etcd for values. This will return the IP addresses and ports of the web containers. 
```
for i in {01..10}; do  etcdctl get /services/web/web$i/unit; etcdctl get /services/web/web$i/host; etcdctl get /services/web/web$i/public_ipv4_addr; etcdctl get /services/web/web$i/port; echo "-----" ; done
monweb@01.service
core01
162.242.254.113
18001
-----
monweb@02.service
core03
162.242.255.71
18002
-----
monweb@03.service
core01
162.242.254.113
18003
-----
monweb@04.service
core03
162.242.255.71
18004
-----
monweb@05.service
core02
162.242.254.215
18005
-----
monweb@06.service
core02
162.242.254.215
18006
-----
monweb@07.service
core01
162.242.254.113
18007
-----
monweb@08.service
core02
162.242.254.215
18008
-----
monweb@09.service
core03
162.242.255.71
18009
-----
monweb@10.service
core04
162.242.255.73
18010
-----
```

 * Test the site on one of the container.
```
curl http://162.242.255.73:18010/home.php
<!DOCTYPE html>
<html>
<body>

<strong>There is no place like 127.0.0.1</strong><br/>Date & Time: 2014-11-13 14:29:18<br/>Container name: dca363b9af75<hr/>  

</body>
</html>
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

 * Now run the lbhelper service. 
```
fleetctl start lbhelper.service 
Unit lbhelper.service launched on 2aa4e35a.../10.208.201.253

fleetctl list-units
UNIT			MACHINE				ACTIVE	SUB
db.service		2aa4e35a.../10.208.201.253	active	running
dbhelper.service	2aa4e35a.../10.208.201.253	active	running
lbhelper.service	2aa4e35a.../10.208.201.253	active	running
mondb.service		2aa4e35a.../10.208.201.253	active	running
monweb@01.service	6847f4f7.../10.208.201.226	active	running
monweb@02.service	ee5398cf.../10.208.201.250	active	running
monweb@03.service	6847f4f7.../10.208.201.226	active	running
monweb@04.service	ee5398cf.../10.208.201.250	active	running
monweb@05.service	c3f52cb3.../10.208.201.234	active	running
monweb@06.service	c3f52cb3.../10.208.201.234	active	running
monweb@07.service	6847f4f7.../10.208.201.226	active	running
monweb@08.service	c3f52cb3.../10.208.201.234	active	running
monweb@09.service	ee5398cf.../10.208.201.250	active	running
monweb@10.service	2aa4e35a.../10.208.201.253	active	running
web@01.service		6847f4f7.../10.208.201.226	active	running
web@02.service		ee5398cf.../10.208.201.250	active	running
web@03.service		6847f4f7.../10.208.201.226	active	running
web@04.service		ee5398cf.../10.208.201.250	active	running
web@05.service		c3f52cb3.../10.208.201.234	active	running
web@06.service		c3f52cb3.../10.208.201.234	active	running
web@07.service		6847f4f7.../10.208.201.226	active	running
web@08.service		c3f52cb3.../10.208.201.234	active	running
web@09.service		ee5398cf.../10.208.201.250	active	running
web@10.service		2aa4e35a.../10.208.201.253	active	running```
```

 * You can look at the logs from it. This container runs a python script that will populate the load balancer with the IP addresses and port numbers from the web containers. The script queries etcd for the information and also does a health check to determine the status of the container.
```
docker logs lbhelper
[11/13/14 14:35:48][INFO]:Authenticated using rtsdemo10
[11/13/14 14:36:32][INFO]:web 01 Found. Processing server
[11/13/14 14:36:32][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:36:32][INFO]:Load balancer pool myworld found
[11/13/14 14:36:32][INFO]:Adding server to load balancer
[11/13/14 14:36:33][INFO]:web 02 Found. Processing server
[11/13/14 14:36:33][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:36:33][INFO]:Load balancer pool myworld found
[11/13/14 14:36:33][INFO]:Adding server to load balancer
[11/13/14 14:36:44][INFO]:web 03 Found. Processing server
[11/13/14 14:36:44][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:36:44][INFO]:Load balancer pool myworld found
[11/13/14 14:36:44][INFO]:Adding server to load balancer
[11/13/14 14:36:55][INFO]:web 04 Found. Processing server
[11/13/14 14:36:55][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:36:55][INFO]:Load balancer pool myworld found
[11/13/14 14:36:55][INFO]:Adding server to load balancer
[11/13/14 14:37:06][INFO]:web 05 Found. Processing server
[11/13/14 14:37:06][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:06][INFO]:Load balancer pool myworld found
[11/13/14 14:37:06][INFO]:Adding server to load balancer
[11/13/14 14:37:12][INFO]:web 06 Found. Processing server
[11/13/14 14:37:12][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:12][INFO]:Load balancer pool myworld found
[11/13/14 14:37:13][INFO]:Adding server to load balancer
[11/13/14 14:37:23][INFO]:web 07 Found. Processing server
[11/13/14 14:37:23][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:23][INFO]:Load balancer pool myworld found
[11/13/14 14:37:24][INFO]:Adding server to load balancer
[11/13/14 14:37:34][INFO]:web 08 Found. Processing server
[11/13/14 14:37:34][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:34][INFO]:Load balancer pool myworld found
[11/13/14 14:37:35][INFO]:Adding server to load balancer
[11/13/14 14:37:45][INFO]:web 09 Found. Processing server
[11/13/14 14:37:45][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:46][INFO]:Load balancer pool myworld found
[11/13/14 14:37:46][INFO]:Adding server to load balancer
[11/13/14 14:37:57][INFO]:web 10 Found. Processing server
[11/13/14 14:37:57][INFO]:Health test passed. Adding to load balancer
[11/13/14 14:37:57][INFO]:Load balancer pool myworld found
[11/13/14 14:37:57][INFO]:Adding server to load balancer
[11/13/14 14:38:08][INFO]:web 11 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 12 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 13 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 14 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 28 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 29 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 30 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 31 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 32 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 33 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 60 does not exist.Skipping...
<truncated>
[11/13/14 14:38:08][INFO]:web 97 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 98 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:web 99 does not exist.Skipping...
[11/13/14 14:38:08][INFO]:Printing summary
[11/13/14 14:38:08][INFO]:Load balancer pool myworld found
[11/13/14 14:38:08][INFO]:Nodes: 1.1.1.1 80
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.113 18001
[11/13/14 14:38:08][INFO]:Nodes: 162.242.255.71 18002
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.113 18003
[11/13/14 14:38:08][INFO]:Nodes: 162.242.255.71 18004
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.215 18005
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.215 18006
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.113 18007
[11/13/14 14:38:08][INFO]:Nodes: 162.242.254.215 18008
[11/13/14 14:38:08][INFO]:Nodes: 162.242.255.71 18009
[11/13/14 14:38:08][INFO]:Nodes: 162.242.255.73 18010
[11/13/14 14:38:08][INFO]:Sleeping 10 seconds...
```

 * This covers our initial exploration of Docker, CoreOS and Fleet.  There is more these tools can do to help with tighter integration but overall this combination is a good way to manage docker containers and run serious workloads on it.


Docker Resource handling
======

This section is more a general review of how resource handling works in containers. Docker uses cgroups to group processes. With cgroups you can manage resources very effectively and this does not apply just to containers. You can do the same with any process. Ultimately with docker, it is a process in a cgroup. On an OS that uses systemd, you can view them using the following.
```
systemd-cgls
```

Tools like free and top are not aware of cgroups. They typically read metrics from the proc filesystem like /proc/meminfo, /proc/vmstat etc.

Also worth noting that , processes inside a container cannot rely on these tools as well as they are subject to limits imposed by the cgroups. To make this worse, /sys/fs/cgroup/memory/memory.stat has a different format to /proc/meminfo. A cgroup specific stuff under /sys/fs/cgroup/cpu/system.slice/<ps name> 

systemd-cgtop command comes handy here.

```
systemd-cgtop
Path                                                                                                                                                                 Tasks   %CPU   Memory  Input/s Output/s

/                                                                                                                                                                       73    2.9   791.1M        -        -
/system.slice                                                                                                                                                            -    2.8   742.1M        -        -
/system.slice/system-sshd.slice                                                                                                                                          4    1.1    24.1M        -        -
/system.slice/etcd.service                                                                                                                                               1    0.9    79.6M       0B   390.8K
/system.slice/fleet.service                                                                                                                                              1    0.7    19.3M        -        -
/system.slice/dbus.service                                                                                                                                               1    0.0     1.0M        -        -
/system.slice/nova-agent-auto.service                                                                                                                                    1    0.0     7.1M        -        -
/system.slice/ntpd.service                                                                                                                                               1    0.0   640.0K        -        -
/system.slice/docker.service                                                                                                                                             1      -   561.5M        -        -
/system.slice/locksmithd.service                                                                                                                                         1      -     7.1M        -        -
/system.slice/nova-agent-watcher.service                                                                                                                                 1      -     4.3M        -        -
/system.slice/system-getty.slice                                                                                                                                         1      -   220.0K        -        -
/system.slice/system-getty.slice/getty@tty1.service                                                                                                                      1      -        -        -        -
/system.slice/system-serial\x2dgetty.slice                                                                                                                               1      -   176.0K        -        -
/system.slice/system-serial\x2dgetty.slice/serial-getty@ttyS0.service                                                                                                    1      -        -        -        -
/system.slice/system-sshd.slice/sshd@552-162.242.254.113:22-212.100.225.42:50254.service                                                                                 4      -        -        -        -
/system.slice/systemd-journald.service                                                                                                                                   1      -    17.6M        -        -
/system.slice/systemd-logind.service                                                                                                                                     1      -   528.0K        -        -
/system.slice/systemd-networkd.service                                                                                                                                   1      -   312.0K        -        -
/system.slice/systemd-resolved.service                                                                                                                                   1      -   260.0K        -        -
/system.slice/systemd-udevd.service                                                                                                                                      1      -     1.2M        -        -
/system.slice/update-engine.service                                                                                                                                      1      -     7.9M        -        -
^C

```

Docker provides some options (See http://docs.docker.com/reference/run/#runtime-constraints-on-cpu-and-memory)

The -c switch specifies CPU shares available to the container.  Every new container get 1024 shares of CPU by default. This is just an abitary number it will only make sense if you change this for a container. For eg. if you have 10 containers on a server with the default share they will all have the same access to CPU time.  However, if 5 of them have 2048, then now you have given those 5 twice the CPU time when compared to other 5.

An interesting fact about Cgroups is that it only limits when needed. So even a lower value of CPU shares will give an container CPU time as long as there is no contention.


Let's build a simple container

```
mkdir  -p loadme
cd loadme
cat <<EOF  >Dockerfile
FROM ubuntu

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

# Update & install packages
RUN apt-get update
RUN apt-get -y -q install stress

EOF

```
```
docker build -t=loadme .
```

Run two different containers with different CPU shares

```
docker run -d --name=avgjoe loadme stress --cpu 2
docker run -d --name=luckyjim -c 2048 loadme stress --cpu 2
```

Now if you look in systemd-cgtop you should see luckyjim using twice the CPU.

```
docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
f50e85039000        loadme:latest       "stress --cpu 2"    7 minutes ago       Up 7 minutes                            luckyjim            
810e7ae95bf9        loadme:latest       "stress --cpu 2"    7 minutes ago       Up 7 minutes                            avgjoe              
```


```
/system.slice                                                                                                                                                            -   98.7   694.6M        -        -
/system.slice/docker-f50e85039000855f17fb02bea2161bd50cd137f7a73b8f40774c4601afe9e58f.scope                                                                              3   63.8     3.1M        -        -
/system.slice/docker-810e7ae95bf9e4a1bb68138f4d5a5946b401b2fc8afb621e093fe421242f3e51.scope                                                                              3   32.0     3.1M        -        -
```

With Memory, docker will allocate all of the RAM by default. To limit it use the -m X switch. This is physical RAM but if the host OS has swap space you can technically allocated more than physical RAM.


This will fail

```
docker run -i -t -m 256m loadme stress --vm 1 --vm-bytes 500M --vm-hang 0
stress: info: [1] dispatching hogs: 0 cpu, 0 io, 1 vm, 0 hdd
stress: FAIL: [1] (416) <-- worker 13 got signal 9
stress: WARN: [1] (418) now reaping child worker processes
stress: FAIL: [1] (422) kill error: No such process
stress: FAIL: [1] (452) failed run completed in 1s
```

As of Nov, 2014 Docker does not allow any way to limit disk IO as far as I can tell. Cgroups does support that and systemd exposes it via BlockIO* options.


Docker API
======

Docker has a good rest API for doing all the things we did via containers. So you can do a lot of this programtically as well.
Here we will cover some basics but for details please refer to  https://docs.docker.com/reference/api/docker_remote_api_v1.15/


 * Just run with the unix socket
```
echo -e "GET /images/json HTTP/1.0\r\n" | nc -U /var/run/docker.sock
```

 * By default docker does not listen on any port and this is by design as the API has no authentication or security feature. Even making it listen on localhost only will expose this to other non-root users. Essentialy anyone with access to that port has full access. 

 * For the sake of our test, lets edit /etc/default/docker.io and add the following. This makes docker listen on that port as well on the usual unix socket. The docker command line by default uses the socker unless the environment variable DOCKER_HOST is specified.

```
DOCKER_OPTS="-H 127.0.0.1:4343 -H unix:///var/run/docker.sock"
```

 * Now curl away :)

``` 
curl -s -XGET http://localhost:4343/images/json
```

 * Run a container
```
docker run -d  centos python -m SimpleHTTPServer 8888
```

 * Keep curling
```
curl -s -XGET http://localhost:4343/containers/json
[{"Command":"python -m SimpleHTTPServer 8888","Created":1416241753,"Id":"5c59ae5bfd6bffb0d73453ffbaf08d9cdc1ca37b9ba6a172e30a09c7d7c58744","Image":"centos:centos7","Names":["/cocky_darwin"],"Ports":[],"Status":"Up 5 seconds"}
```

```
 curl -s -XGET http://localhost:4343/containers/5c59ae5bfd6bffb0d73453ffbaf08d9cdc1ca37b9ba6a172e30a09c7d7c58744/json | python -m json.tool |head -30
{
    "Args": [
        "-m",
        "SimpleHTTPServer",
        "8888"
    ],
    "Config": {
        "AttachStderr": false,
        "AttachStdin": false,
        "AttachStdout": false,
        "Cmd": [
            "python",
            "-m",
            "SimpleHTTPServer",
            "8888"
        ],
        "CpuShares": 0,
        "Cpuset": "",
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "ExposedPorts": null,
        "Hostname": "5c59ae5bfd6b",
        "Image": "centos",
        "Memory": 0,
        "MemorySwap": 0,
        "NetworkDisabled": false,
        "OnBuild": null,
```

```
curl -s -XGET http://localhost:4343/containers/5c59ae5bfd6bffb0d73453ffbaf08d9cdc1ca37b9ba6a172e30a09c7d7c58744/top | python -m json.tool |head -30
{
    "Processes": [
        [
            "root",
            "10783",
            "10406",
            "0",
            "16:29",
            "?",
            "00:00:00",
            "python -m SimpleHTTPServer 8888"
        ]
    ],
    "Titles": [
        "UID",
        "PID",
        "PPID",
        "C",
        "STIME",
        "TTY",
        "TIME",
        "CMD"
    ]
}
```

Docker volumes
======

Docker containers by default don't hold the data till you commit the top most layer back to the image. Docker also provides support for volumes which allows storing persistent data. 


 * You can mount a file or folder to the container. For e.g. Share a file from the host. This can be applied to directories as well. 

```
docker run --rm -it -v ~/.bash_history:/.bash_history ubuntu /bin/bash

root@a45e2edce0b7:/# history |tail -10
==> standard input <==
  187  ls /var/run/docker.
  188  docker stop $(docker ps -a -q)
  189  sleep 2
  190  mkdir /vol1
  191  docker run -i -t -v /vol1 ubuntu /bin/bash
  192  docker run -i -t -v /vol2 ubuntu /bin/bash
  193  ls /var/lib/docker/container
  194  ls /var/lib/docker/containers
  195  docker run --rm -it -v ~/.bash_history:/.bash_history ubuntu /bin/bash
  196  history |tail - 10

root@a45e2edce0b7:/# exit
exit

```


 * You can also create docker volumes that is independant from the container's UFS file system. These can can be shared and reused between containers. They also are not deleted till the last container using them has been deleted. They are not included in the image either. So they are good place for persistent data. Here's a quick example


```
docker run -d --name db1 --volume /dbvol1 ubuntu /bin/bash -c 'i=0; while true; do echo "Writing file $i";  echo $i > /dbvol1/data-$i ;  i=$((i+1)) ; echo "Sleeping..."; sleep 10; done'
```

 * Watch the logs
```
docker logs -f db1
Writing file 0
Sleeping...
Writing file 1
Sleeping...
```

 * Start another server that is attached to the volume we created above
```
 docker run -t -i --volumes-from db1 --name db2 centos /bin/bash

bash-4.2# df
Filesystem     1K-blocks     Used Available Use% Mounted on
rootfs          29617196 13549636  14758480  48% /
none            29617196 13549636  14758480  48% /
tmpfs           16456924        0  16456924   0% /dev
shm                65536        0     65536   0% /dev/shm
/dev/sda1       29617196 13549636  14758480  48% /dbvol1
tmpfs            3291388      760   3290628   1% /etc/resolv.conf
tmpfs           16456924        0  16456924   0% /proc/kcore

bash-4.2# ls /dbvol1/
data-0	data-1	data-2	data-3

bash-4.2# exit
exit
```

 * You review the data on the host as well.

```
docker inspect -f '{{.Volumes}}' db1
map[/dbvol1:/var/lib/docker/vfs/dir/d57a5f23cacd36721ac6fc15386e78d1a39621cebcfc2d46fbe81dec2a0f1ff6]

ls /var/lib/docker/vfs/dir/d57a5f23cacd36721ac6fc15386e78d1a39621cebcfc2d46fbe81dec2a0f1ff6
```

Use of volumes does bind the container to the host. Volumes can be migrated to other hosts but they need manual steps. Docker also does not provide any easy way to manage these volumes (there is no docker volumes). These volumes will stay the host till you delete every container that used it. The container need not be running (volumes are persistent).



Misc Commands
======

A collection of random snippets that are useful.

 * Build without cache. This burnt me the first time. Ubuntu removes old package versions from their repos and if a cached image has that version, apt-get install will try to pull that and fail. Needless to say --no-cache will take longer to build.

```
docker build --no-cache
```

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

 * A good overview on why docker was created. Done by dotCloud founder and CTO Solomon Hykes - https://www.youtube.com/watch?v=Q5POuMHxW-0  - 

 * http://www.flockport.com/lxc-vs-docker/

 * https://developer.rackspace.com/blog/running-coreos-and-kubernetes/

 * RESOURCE MANAGEMENT WITH CONTROL GROUPS - https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Resource_Management_and_Linux_Containers_Guide/index.html

 * Docker security article - https://docs.docker.com/articles/security/

 * Getting Started with systemd - https://coreos.com/docs/launching-containers/launching/getting-started-with-systemd/

 * Docker API - https://docs.docker.com/reference/api/docker_remote_api_v1.15/

Tools
======
 * Fig http://www.fig.sh/

 * Kubernetes https://github.com/GoogleCloudPlatform/kubernetes

 * Flocker https://github.com/ClusterHQ/flocker

 * Boot2Docker https://github.com/boot2docker/boot2docker

 * Apache mesos http://mesos.apache.org/


Credits
======
 * Simone Soldateschi - https://github.com/siso

 * Kyle Kelley - https://github.com/rgbkrk
 
 * tmpnb - https://github.com/jupyter/tmpnb

