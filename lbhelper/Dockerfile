FROM ubuntu:12.04

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

# Update & install packages
RUN apt-get update
RUN apt-get install -y curl python-setuptools python-pip less vim

# Install pyrax
RUN pip install pyrax termcolor

# Script that creates a db file
ADD ./usr/local/bin/config.py /usr/local/bin/config.py
ADD ./usr/local/bin/utils.py /usr/local/bin/utils.py
ADD ./usr/local/bin/lbmanage.py /usr/local/bin/lbmanage.py

# Script that starts supervisord
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
