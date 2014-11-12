#!/usr/bin/env bash

# this is needed for the script to communicate with etcd
ROUTER_IP=$(/sbin/ip route | awk '/default/ { print $3 }')
echo $ROUTER_IP etcd_host >> /etc/hosts

/usr/bin/python /usr/local/bin/lbmanage.py
