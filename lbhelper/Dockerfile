FROM ubuntu:12.04

# Some basic things to make sure the image is happy
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl
ENV DEBIAN_FRONTEND noninteractive

# Update & install packages
RUN apt-get update
RUN apt-get install -y curl python-setuptools python-pip less vim

# Install pyrax via pip
RUN pip install pyrax termcolor

# copy our lb addition code. This could also be pulled from a git repo
ADD ./usr/local/bin/config.py /usr/local/bin/config.py
ADD ./usr/local/bin/utils.py /usr/local/bin/utils.py
ADD ./usr/local/bin/lbmanage.py /usr/local/bin/lbmanage.py

# Copy the startup script
ADD ./usr/local/bin/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

# Run it
CMD ["/usr/bin/env", "bash", "/usr/local/bin/start.sh"]
