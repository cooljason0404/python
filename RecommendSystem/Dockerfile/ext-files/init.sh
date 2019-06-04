#!/bin/bash

##
#mkdir -p /mnt/cifs
#echo "//192.168.123.150/homes/home /mnt/cifs cifs rw,suid,dir_mode=0777,file_mode=0666,username=home,password=home,vers=1.0  0 0" > /etc/fstab
#mount -a

## sync remote file/scripts to locak/workspace
rsync -vzrtopg --progress --delete /mnt/cifs/* /var/workspace/spark/
