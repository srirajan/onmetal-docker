#!/bin/bash

/usr/bin/mysqld_safe > /dev/null 2>&1 &

RET=1
while [[ RET -ne 0 ]]; do
    sleep 5
    mysql -uroot -e "status" > /dev/null 2>&1
    RET=$?
done
    mysql_install_db > /dev/null 2>&1
    mysql -e "create database if not exists ${DB_NAME}"
    curl -o /tmp/world_innodb.sql https://raw.githubusercontent.com/RackspaceDevOps/demos/master/mysql_db/world_innodb.sql
    mysql -h 127.0.0.1 -P  3306 ${DB_NAME} < /tmp/world_innodb.sql
    mysql -h 127.0.0.1 -P  3306 -e "GRANT ALL on ${DB_NAME}.* to '${DB_USER}'@'%'"
    mysql -h 127.0.0.1 -P  3306 -e "SET PASSWORD for '${DB_USER}@'%' = PASSWORD('${DB_PW}')"
    mysqladmin shutdown
