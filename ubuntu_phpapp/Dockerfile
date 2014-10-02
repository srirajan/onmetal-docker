#adapted from https://github.com/siso/docker-php/blob/master/Dockerfile

FROM ubuntu:14.04

# Keep upstart from complaining
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl

# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get dist-upgrade -y

# install basic packages
RUN apt-get install -y nginx php5-cli php5-fpm python-setuptools

# tell Nginx to stay foregrounded
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# nginx site conf
ADD ./etc/nginx/sites-available/default/example.conf /etc/nginx/sites-available/default

# php-fpm config
RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf
RUN sed -i -e "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/g" /etc/php5/fpm/php.ini
RUN sed -i -e "s/post_max_size\s*=\s*8M/post_max_size = 100M/g" /etc/php5/fpm/php.ini
RUN sed -i -e "s/;catch_workers_output\s*=\s*yes/catch_workers_output = yes/g" /etc/php5/fpm/pool.d/www.conf

# php files
ADD ./usr/share/nginx/html/index.php /usr/share/nginx/html/

# Supervisor Config
RUN /usr/bin/easy_install supervisor
RUN /usr/bin/easy_install supervisor-stdout
ADD ./etc/supervisord.conf /etc/supervisord.conf

# startup script
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

EXPOSE 80

CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
