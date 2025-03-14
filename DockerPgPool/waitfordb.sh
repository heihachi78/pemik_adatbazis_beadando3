#!/bin/bash

set -e

check_retry_count () {
    RETRY_COUNT=$1
    MAX_RETRY=12
    failed_db_host=$2  
    
    if [ $RETRY_COUNT -eq $MAX_RETRY ]; then
        echo "$failed_db_host is unreachable"
        exit 3
    fi
}

db_host_names=$NODES

for str in ${db_host_names[*]}; do
    RETRY_COUNT=0
    until nc -z $str 5432; do
        check_retry_count $RETRY_COUNT $str
        ((RETRY_COUNT=RETRY_COUNT+1))
        echo "waiting for $str"
        sleep 5s
    done
  echo "$str host is ready"
done
echo "all host is ready"
exec "$@"
