#!/bin/bash

## sync remote file/scripts to locak/workspace
rsync -vzrtopg --progress --delete /mnt/cifs/* /var/workspace/spark/

## start train
python -u /var/workspace/spark/train.py