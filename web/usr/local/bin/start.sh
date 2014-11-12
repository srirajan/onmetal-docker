#!/usr/bin/env bash

# THis is needed to query etcd
ROUTER_IP=$(/sbin/ip route | awk '/default/ { print $3 }')
echo $ROUTER_IP etcd_host >> /etc/hosts

/usr/local/bin/configuredb.sh

/usr/local/bin/supervisord -n
