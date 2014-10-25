# Install apache
FROM ubuntu:14.04
RUN apt-get update && apt-get install -y apache2

ENV APACHE_SERVERNAME helloworld.example.com
ENV APACHE_SERVERADMIN admin@localhost
ENV APACHE_DOCUMENTROOT /var/www/html
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]

