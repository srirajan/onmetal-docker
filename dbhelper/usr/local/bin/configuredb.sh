#!/bin/bash

echo "Creating the world database"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${APP_DB_NAME}"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} ${APP_DB_NAME} < /tmp/world_innodb.sql
echo "Creating application user"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "GRANT ALL on ${APP_DB_NAME}.* to '${APP_USER}'@'%'"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "SET PASSWORD for '${APP_USER}'@'%' = PASSWORD('${APP_PW}')"
echo "Counting rows in world.city"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_MYSQL_ROOT_PASSWORD} -e "SELECT COUNT(*) from world.City"

while true
do
  # loop infinitely
done