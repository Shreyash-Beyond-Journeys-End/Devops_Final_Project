#!/bin/bash
# sends a lot of requests to the app so the grafana graphs and the HPA have something to show
# usage: ./scripts/load-test.sh <url> [seconds]
# example: ./scripts/load-test.sh http://placetrack.local 60

URL=$1
SECONDS_TO_RUN=${2:-60}

if [ -z "$URL" ]; then
  echo "usage: ./scripts/load-test.sh <url> [seconds]"
  exit 1
fi

# get the ids of jobs that exist, so we don't make 404 errors
IDS=$(curl -s "$URL/api/jobs" | grep -o '"id":[0-9]*' | cut -d: -f2)
if [ -z "$IDS" ]; then
  echo "no jobs found, add some in the app first"
  exit 1
fi
IDS=($IDS)
echo "found ${#IDS[@]} jobs, sending requests for $SECONDS_TO_RUN seconds"

END=$((SECONDS + SECONDS_TO_RUN))
while [ $SECONDS -lt $END ]; do
  curl -s -o /dev/null "$URL/api/jobs" &
  curl -s -o /dev/null "$URL/api/jobs/stats" &
  for i in 1 2 3; do
    ID=${IDS[$RANDOM % ${#IDS[@]}]}
    curl -s -o /dev/null "$URL/api/jobs/$ID" &
  done
  wait
  sleep 0.1
done
echo "finished"
