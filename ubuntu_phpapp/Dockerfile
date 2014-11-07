FROM ubuntu:14.04

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

#Install packages
RUN apt-get update
RUN apt-get install -y nginx php5-cli php5-fpm python-setuptools vim

# tell Nginx to stay foregrounded
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Copy the website configuration for Nginx
ADD ./etc/nginx/sites-available/default/example.conf /etc/nginx/sites-available/default

# Un-Daemonize php-fpm 
RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf

# Install Supervisor & configure
RUN /usr/bin/easy_install supervisor
RUN /usr/bin/easy_install supervisor-stdout
ADD ./etc/supervisord.conf /etc/supervisord.conf

# Copy a sample PHP file
ADD ./usr/share/nginx/html/home.php /usr/share/nginx/html/

# Open port 80 on the container
EXPOSE 80

# Script that starts supervisord
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
