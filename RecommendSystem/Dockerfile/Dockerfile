# Author: Jason Wu

FROM centos:7

## Maintainer
MAINTAINER Jason cooljason0404@gmail.com

RUN yum -y install epel-release
RUN yum -y update
RUN yum install -y nano wget htop which

## install spark
RUN yum -y install python-pip

## install numpy requests
RUN pip install --upgrade pip
RUN pip install pyspark numpy requests

## install java
RUN yum -y install java-1.8.0-openjdk

## config java path
RUN export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64/jre/bin/java
RUN export JRE_HOME=$JAVA_HOME/jre
RUN export CLASSPATH=$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH
RUN export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH

## mount network file system (cifs)
RUN yum install -y samba-client samba-common cifs-utils rsync

## init script
RUN mkdir -p /var/init
ADD ./ext-files/init.sh /var/init/
ADD ./ext-files/train.sh /var/init/
ADD ./ext-files/prediction.sh /var/init/
RUN chmod +x /var/init/init.sh
RUN chmod +x /var/init/train.sh
RUN chmod +x /var/init/prediction.sh

RUN ln -s /var/init/train.sh /bin/train
RUN ln -s  /var/init/prediction.sh /bin/prediction 

## workspace
RUN mkdir -p /var/workspace/spark
RUN mkdir -p /var/workspace/run