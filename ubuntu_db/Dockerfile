FROM ubuntu:14.04

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive


# Update & install packages
RUN apt-get update
RUN apt-get install -yq  mysql-server-5.6  mysql-client-5.6 curl

RUN curl -o /tmp/world_innodb.sql https://raw.githubusercontent.com/RackspaceDevOps/demos/master/mysql_db/world_innodb.sql
RUN mysql -e 'create database if not exists world'
RUN mysql world < /tmp/world_innodb.sql
RUN mysql -e "GRANT ALL on world.* to 'app'@'%'"
RUN mysql -e "SET PASSWORD for 'app'@'%' = PASSWORD('4dfjru4Djhedk33')"

# Exposed ENV
ENV DB_USER app
ENV DB_PW 4dfjru4Djhedk33
ENV DB_PORT 3306

# Add VOLUMEs to allow backup of config and databases
VOLUME  ["/var/lib/mysql"]

EXPOSE 3306
CMD ["/usr/bin/mysqld_safe"]