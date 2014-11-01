#!/usr/bin/env bash

ROUTER_IP=$(/sbin/ip route | awk '/default/ { print $3 }')

echo $ROUTER_IP etcd_host >> /etc/hosts

# start all the services
/usr/local/bin/supervisord -n
