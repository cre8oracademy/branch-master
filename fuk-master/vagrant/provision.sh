#!/usr/bin/env bash

# Provision an ubuntu 12.04 precise 64bit server
# for running fuk.co.uk

# Does a reasonable job running on an already-configured server, 
# but probably best to use --no-provision to save time.

export DEBIAN_FRONTEND=noninteractive
apt-get update > /dev/null

# set mysql root password

# echo mysql-server mysql-server/root_password password ticketyboo | sudo debconf-set-selections
# echo mysql-server mysql-server/root_password_again password ticketyboo | sudo debconf-set-selections

apt-get -y install build-essential git-core nginx curl mysql-server \
libmysqlclient15-dev python-dev python-setuptools

apt-get -y build-dep python-imaging

easy_install pip
pip install virtualenv
pip install supervisor

# symlink image libraries so that PIL can find them.

test -e /usr/lib/libfreetype.so || ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
test -e /usr/lib/libjpeg.so || ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
test -e /usr/lib/libz.so || ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
