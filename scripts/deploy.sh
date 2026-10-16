#!/bin/bash
# deploys the app to the current kubectl cluster with helm
# usage: ./scripts/deploy.sh <image tag (commit sha)>
set -e

TAG=$1
if [ -z "$TAG" ]; then
  echo "usage: ./scripts/deploy.sh <image tag>"
  exit 1
fi

kubectl apply -f k8s/namespace.yaml

# --reuse-values keeps settings from before (like serviceMonitor.enabled)
helm upgrade --install placetrack helm/placetrack \
  -n placetrack \
  --reuse-values \
  --set image.tag="$TAG" \
  --wait --timeout 5m

kubectl -n placetrack get pods
