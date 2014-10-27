FROM mysql

# Database environment
ENV DB_NAME world
ENV DB_USER app
ENV DB_PW 4dfjru4Djhedk33
ENV DB_PORT 3306

EXPOSE 3306

ADD ./usr/local/bin/configure.sh /usr/local/bin/configure.sh
RUN chmod 755 /usr/local/bin/configure.sh
RUN /usr/local/bin/configure.sh
