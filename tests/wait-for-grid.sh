#!/bin/bash
# wait-for-grid.sh

set -e
se_endpoint=${SE_ENDPOINT:-"localhost:4444"}
url="http://${se_endpoint}/wd/hub/status"
wait_interval_in_seconds=1
max_wait_time_in_seconds=60
end_time=$((SECONDS + max_wait_time_in_seconds))
time_left=$max_wait_time_in_seconds
cmd="$@"

while [ $SECONDS -lt $end_time ]; do
    response=$(curl -sL "$url" | jq -r '.value.ready')
    if [ -n "$response"  ]  && [ "$response" ]; then        
        break
    else
        echo "Waiting for the Grid at $url. Sleeping for $wait_interval_in_seconds second(s). $time_left seconds left until timeout."
        sleep $wait_interval_in_seconds
        time_left=$((time_left - wait_interval_in_seconds))
    fi
done

if [ $SECONDS -ge $end_time ]; then
    echo "Timeout: The Grid was not started within $max_wait_time_in_seconds seconds."
    exit 1
fi

echo "Selenium Grid is up - executing tests"
exec $cmd
