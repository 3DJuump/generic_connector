#!/bin/sh
# exit in case of error
set -e
mountpoint "/connector" 2>&1 >/dev/null
ret=$?
if [ $ret -ne 0 ]; then
	echo "/connector should be a mounted folder !!"
	exit 1
fi

/usr/bin/python3 /init.py
/usr/bin/python3 /connector/_scripts/meta_connector.py
#sleep 500000000000000000000000000000000000000


