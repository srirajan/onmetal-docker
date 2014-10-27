FROM ubuntu:14.04

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

# Database environment
ENV DB_NAME world
ENV DB_USER app
ENV DB_PW 4dfjru4Djhedk33
ENV DB_PORT 3306

# Update & install packages
RUN apt-get update
RUN apt-get -y -q install   mysql-server-5.6  mysql-client-5.6 curl

RUN /usr/bin/mysqld_safe > /dev/null 2>&1 &
RUN sleep 5
RUN mysql -e "create database if not exists $DB_NAME"
RUN curl -o /tmp/world_innodb.sql https://raw.githubusercontent.com/RackspaceDevOps/demos/master/mysql_db/world_innodb.sql
RUN mysql $DB_NAME < /tmp/world_innodb.sql
RUN mysql -e "GRANT ALL on world.* to 'app'@'%'"
RUN mysql -e "SET PASSWORD for 'app'@'%' = PASSWORD('4dfjru4Djhedk33')"
RUN mysqladmin shutdown

# Add VOLUMEs to allow backup of config and databases
VOLUME  ["/var/lib/mysql"]

EXPOSE 3306

CMD ["/usr/bin/mysqld_safe"]