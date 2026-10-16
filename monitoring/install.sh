#!/bin/bash
# installs prometheus + grafana (kube-prometheus-stack) and my placetrack dashboard
# run from the project root: ./monitoring/install.sh
#
# grafana password:
# kubectl -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d
set -e

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# make a random grafana password, only the first time
if ! kubectl -n monitoring get secret grafana-admin > /dev/null 2>&1; then
  kubectl -n monitoring create secret generic grafana-admin \
    --from-literal=admin-user=admin \
    --from-literal=admin-password="$(openssl rand -hex 16)"
fi

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --version 92.1.1 \
  -n monitoring \
  -f monitoring/values.yaml \
  --wait --timeout 10m

# dashboard as a configmap, the grafana sidecar loads it
kubectl -n monitoring create configmap placetrack-dashboard \
  --from-file=placetrack.json=monitoring/grafana-dashboard.json \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n monitoring label configmap placetrack-dashboard grafana_dashboard=1 --overwrite

echo "done"
