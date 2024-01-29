kubectl create ns locust

kubectl create configmap my-loadtest-locustfile --from-file ./main.py -n locust
kubectl create configmap my-loadtest-lib --from-file ./lib -n locust

kubectl apply -f role.yaml 

helm install locust deliveryhero/locust \
  --set loadtest.name=my-loadtest0 \
  --set loadtest.locust_locustfile_configmap=my-loadtest-locustfile \
  --set loadtest.locust_lib_configmap=my-loadtest-lib  -f values.yaml -n locust


