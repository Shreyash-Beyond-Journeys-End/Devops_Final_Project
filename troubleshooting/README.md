# Troubleshooting practice

I broke 2 things on purpose in the `placetrack` namespace on minikube and then fixed them.
For both I followed the same steps: find the problem, check details, find the cause, fix, check again.

Screenshots: [bad image tag](../images/18-ts-image-error.png), [wrong service selector](../images/19-ts-selector.png)

## 1. Wrong image tag (broken-image.yaml)

```
kubectl apply -f troubleshooting/broken-image.yaml
```

**Problem:** the pod never becomes ready.

```
$ kubectl -n placetrack get pods -l app=tb-image
NAME                        READY   STATUS             RESTARTS   AGE
tb-image-66bd864fb6-qb4v6   0/1     ImagePullBackOff   0          51s
```

**Details:** `kubectl describe pod` shows the events at the bottom:

```
Warning  Failed   kubelet  Failed to pull image "ghcr.io/shreyash-beyond-journeys-end/placetrack-backend:does-not-exist": ... not found
Warning  Failed   kubelet  Error: ErrImagePull
Normal   BackOff  kubelet  Back-off pulling image "ghcr.io/shreyash-beyond-journeys-end/placetrack-backend:does-not-exist"
Warning  Failed   kubelet  Error: ImagePullBackOff
```

**Cause:** the tag `does-not-exist` is not in GHCR, so the image can't be downloaded and the container never starts.
So the problem is in the yaml, not in my app code.

**Fix:** use a tag that the pipeline really pushed (a commit SHA):

```
$ kubectl -n placetrack set image deploy/tb-image app=ghcr.io/shreyash-beyond-journeys-end/placetrack-backend:da065ae8e472120944eef94265b25cd04d4be71c
deployment.apps/tb-image image updated
$ kubectl -n placetrack rollout status deploy/tb-image --timeout=60s
deployment "tb-image" successfully rolled out
```

**Check:** new pod is running and the old one is going away.

```
$ kubectl -n placetrack get pods -l app=tb-image
NAME                        READY   STATUS        RESTARTS   AGE
tb-image-66bd864fb6-qb4v6   0/1     Terminating   0          52s
tb-image-7c694d6677-4bnph   1/1     Running       0          1s
```

## 2. Service selector does not match (broken-service.yaml)

```
kubectl apply -f troubleshooting/broken-service.yaml
```

**Problem:** the pod is Running but the service has no endpoints, so nothing can reach the pod through the service.

```
$ kubectl -n placetrack get endpoints tb-svc
NAME     ENDPOINTS   AGE
tb-svc   <none>      84s
```

**Details:** compare the service selector with the pod labels.

```
$ kubectl -n placetrack get svc tb-svc -o jsonpath='{.spec.selector}'
{"app":"tb-service"}
$ kubectl -n placetrack get pods -l app=tb-svc --show-labels
NAME                      READY   STATUS    RESTARTS   AGE   LABELS
tb-svc-746b6b6cc6-gnkw4   1/1     Running   0          84s   app=tb-svc,pod-template-hash=746b6b6cc6
```

**Cause:** the service looks for `app=tb-service` but the pod has `app=tb-svc`. They must match exactly.

**Fix:**

```
$ kubectl -n placetrack patch svc tb-svc -p '{"spec":{"selector":{"app":"tb-svc"}}}'
service/tb-svc patched
```

**Check:** the endpoint now has the pod IP.

```
$ kubectl -n placetrack get endpoints tb-svc
NAME     ENDPOINTS        AGE
tb-svc   10.244.0.20:80   86s
```

Clean up after:

```
kubectl delete -f troubleshooting/broken-image.yaml -f troubleshooting/broken-service.yaml
```
