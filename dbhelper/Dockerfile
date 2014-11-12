FROM ubuntu

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

# Database environment
ENV APP_DB_NAME world
ENV APP_USER app
ENV APP_PW 4dfjru4Djhedk33

# Update & install packages
RUN apt-get update
RUN apt-get -y -q install curl mysql-client

# Download the database into the container
ADD world_innodb.sql /tmp/world_innodb.sql

# Start the script
ADD ./usr/local/bin/configuredb.sh /usr/local/bin/configuredb.sh
RUN chmod 755 /usr/local/bin/configuredb.sh
