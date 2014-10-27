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

#copy our my.cnf
ADD ./etc/mysql/my.cnf /etc/mysql/conf.d/my.cnf 

#simplified start script
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

# Add VOLUMEs to allow backup of config and databases
VOLUME  ["/var/lib/mysql"]

EXPOSE 3306

CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
