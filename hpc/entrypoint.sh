#!/usr/bin/env bash
export SRM_PATH=/opt/srmclient-2.6.28/usr/share/srm
export PATH=/opt/srmclient-2.6.28/usr/bin:$PATH

/var/local/download.py $1 $PWD