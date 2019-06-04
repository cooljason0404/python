#!/bin/bash

## sync remote file/scripts to locak/workspace
rsync -vzrtopg --progress --delete /mnt/cifs/* /var/workspace/spark/

## start tumbler
python -u /var/workspace/spark/tumbler.py