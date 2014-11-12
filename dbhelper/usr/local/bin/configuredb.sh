#!/bin/bash

while ! curl http://$DB_PORT_3306_TCP_ADDR:$DB_PORT_3306_TCP_PORT/ >/dev/null 2>&1
do
  sleep 2
  echo "Waiting for database server..."
done

sleep 5

echo "Creating the world database"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${APP_DB_NAME}"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} ${APP_DB_NAME} < /tmp/world_innodb.sql

echo "Creating application user"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "GRANT ALL on ${APP_DB_NAME}.* to '${APP_USER}'@'%'"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "SET PASSWORD for '${APP_USER}'@'%' = PASSWORD('${APP_PW}')"

echo "Counting rows in world.city"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "SELECT COUNT(*) from world.City"

# loop infinitely
while true
do
 sleep 10
done
