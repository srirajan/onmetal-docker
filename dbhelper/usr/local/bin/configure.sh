#!/bin/bash

mysql -e "create database if not exists ${DB_NAME}"
curl -o /tmp/world_innodb.sql https://raw.githubusercontent.com/RackspaceDevOps/demos/master/mysql_db/world_innodb.sql
mysql -h 127.0.0.1 -P  3306 ${DB_NAME} < /tmp/world_innodb.sql
mysql -h 127.0.0.1 -P  3306 -e "GRANT ALL on ${DB_NAME}.* to '${DB_USER}'@'%'"
mysql -h 127.0.0.1 -P  3306 -e "SET PASSWORD for '${DB_USER}@'%' = PASSWORD('${DB_PW}')"
