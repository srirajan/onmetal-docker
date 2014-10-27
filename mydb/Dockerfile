FROM mysql

# Database environment
ENV APP_DB_NAME world
ENV APP_USER app
ENV APP_USER 4dfjru4Djhedk33
ENV APP_LOAD_DB 1

RUN apt-get -y -q install curl

EXPOSE 3306

COPY entrypoint.sh /entrypoint.sh

RUN curl -o /tmp/world_innodb.sql https://raw.githubusercontent.com/RackspaceDevOps/demos/master/mysql_db/world_innodb.sql

RUN /usr/bin/mysqld_safe & && \
  sleep 5 && \
  mysql -u root world < /tmp/world_innodb.sql 

ENTRYPOINT ["/entrypoint.sh"]

