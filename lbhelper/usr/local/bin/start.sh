#!/usr/bin/env bash

ROUTER_IP=$(/sbin/ip route | awk '/default/ { print $3 }')

echo $ROUTER_IP etcd_host >> /etc/hosts

/usr/bin/python /usr/local/bin/lbmanage.py
