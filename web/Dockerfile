FROM ubuntu:14.04

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
RUN apt-get install -y nginx mysql-client php5-cli php5-fpm python-setuptools vim php5-mysql

# tell Nginx to stay foregrounded
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Copy the website configuration for Nginx
ADD ./etc/nginx/sites-available/default/example.conf /etc/nginx/sites-available/default

# Un-Daemonize php-fpm 
RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf

# Install Supervisord & copy configuration file
RUN /usr/bin/easy_install supervisor
RUN /usr/bin/easy_install supervisor-stdout
ADD ./etc/supervisord.conf /etc/supervisord.conf

# Copy PHP files
ADD ./usr/share/nginx/html/home.php /usr/share/nginx/html/home.php
ADD ./usr/share/nginx/html/db_host.php /usr/share/nginx/html/db_host.php
ADD ./usr/share/nginx/html/health.php /usr/share/nginx/html/health.php
ADD ./usr/share/nginx/html/world.php /usr/share/nginx/html/world.php

# Open port 80 on the container
EXPOSE 80

# Script that creates the db configuration needed for php
ADD ./usr/local/bin/configuredb.sh /usr/local/bin/configuredb.sh
RUN chmod 755 /usr/local/bin/configuredb.sh

# Copy start up script
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

# Run
CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
