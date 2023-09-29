#!/bin/bash
# wait-for-sc.sh

set -e

cmd="$@"

while [ ! -f /tmp/sc.ready ]
do
  echo 'Waiting for SC...'
  sleep 2
done

echo 'SC is ready. Running tests!'
exec $cmd