Docker
=====

 * Build a Ubuntu 14.04 server
```
key=sri-key
nova boot --flavor general1-1 \
--image  a1558fdc-3182-4a0f-b48a-aa900a5826c3 \
--key-name $key \
--poll play01
```

 * Install docker on Ubuntu (play01 above)
```
nova ssh play01 --network=public
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


CoreOS, Fleet & Docker
=====

 * Prepare CoreOS cluster. Before we do other stuff, let's spin up some core OS servers. First get a discovery URL for your cluster. More on this at https://coreos.com/docs/cluster-management/setup/cluster-discovery/

```
curl -w "\n" https://discovery.etcd.io/new
```

 * Edit the cloud init file named coreos-cluster/cloudinit.yaml. Replace the token url from above.


 * Boot 4 servers for the cluster
```
# Performance 
flavor=general1-1
image=05438eb5-af42-4bdd-bd32-309c2154927d
key=sri-key
cloudinit=cloudinit.yaml

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core01

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core02

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core03

nova boot --flavor $flavor --image $image  --key-name $key \
--config-drive true --user-data $cloudinit core04
```


 * Login to and test

```
nova ssh core01 --network=public

fleetctl list-machines
```
  
 * Pull our repo on one of the nodes.
```
git clone https://github.com/srirajan/onmetal-docker
```

 * Review and load all the services. We wlll go into details of each service in following steps.
```
cd /root/onmetal-docker/fleet-services
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
```

 * This covers our initial exploration of Docker, CoreOS and Fleet.  There is more these tools can do to help with tighter integration but overall this combination is a good way to manage docker containers and run serious workloads on it.
