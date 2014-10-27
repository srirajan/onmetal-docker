#!/bin/bash

MYSQL_DATADIR="/var/lib/mysql"

/usr/bin/mysqld_safe > /dev/null 2>&1 &
RET=1
while [[ RET -ne 0 ]]; do
    sleep 5
    mysql -uroot -e "status" > /dev/null 2>&1
    RET=$?
done

if [[ ! -d $MYSQL_DATADIR/mysql ]]; then
    /usr/local/bin/configure.sh
fi

exec mysqld_safe