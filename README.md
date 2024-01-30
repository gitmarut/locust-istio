# Locust-istio

Python scripts to enable Locust to send traffic to a istio ingressgateway which will handle traffic for multiple hostnames.

## Rationale
Some challenges I faced while using locust to test traffic on istio service mesh.

1. In a development test setup these hostname may not get resolved by DNS. So traffic need to resolve IP address manually like in "--connect-to" flag in curl
 
2. Many times traffic is sent to a ClusterIP service or a NodePort service (if user does not want a waste a LB from their LB pool.

3. Deployment of locust in Kubernetes is not an easy method.

These python files will enable locust to handle these challenges. Also Helm is used to address the challenge of deployment in Kubernetes.

LoadBalancer example with curl:

    curl https://bookinfo.example.com/productpage --connect-to bookinfo.example.com:443:**LB-IP**:443

NodePort example with curl: 

    curl https://bookinfo.example.com/productpage --connect-to bookinfo.example.com:443:**Node-IP**:**Nodeport-for-port-443**

ClusterIP example with curl: 

    curl https://bookinfo.example.com/productpage --connect-to bookinfo.example.com:443:**ClusterIP**:443

## Installation and Test steps
### Creating test setup

For creating a test setup I used documentation given in "https://istio.io/latest/docs/setup/getting-started/". For ease of reference

    curl -L https://istio.io/downloadIstio | sh -
    cd istio-1.20.2
    export PATH=$PWD/bin:$PATH
    istioctl install --set profile=demo -y

	kubectl create ns bookinfo0
	kubectl create ns bookinfo1
    kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml -n bookinfo0
    kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml -n bookinfo1

Currently main script assumes "istio-ingressgateway" pod runs in istio-system namespace and associated gateways are installed in istio-system namespace.
 
In the main script edit the sections "#getting service details" and "#getting hostnames" to change to your custom namespace, service and gateway labels.
For testing the script use the example given in "bookinfo-gateway-vs.yaml" & "aegle-wildcard-secret.yaml".

    kubectl apply -f aegle-wildcard-secret.yaml
    kubectl apply -f bookinfo-gateway-vs.yaml

### Install locust

    kubectl create ns locust
    
    kubectl create configmap my-loadtest-locustfile --from-file ./main.py -n locust
    kubectl create configmap my-loadtest-lib --from-file ./lib -n locust
    
    kubectl apply -f role.yaml
    
    helm install locust deliveryhero/locust \
      --set loadtest.name=my-loadtest0 \
      --set loadtest.locust_locustfile_configmap=my-loadtest-locustfile \
      --set loadtest.locust_lib_configmap=my-loadtest-lib  -f values.yaml -n locust

### Start locust traffic
1. Check locust master and worker pods are coming up. 
2. If there is a crash check the log outputs of pods and fix the python scripts if needed. Or if it is a infra (kubernetes / istio) related problem, fix it.
3. If the python scripts are changed to fix step 2, unistall the helm and the configmaps used for installation. Redo the installation.
4. Once pods are up you can port-forward the locust service and use browser to start test or monitor it as given.
 `kubectl port-forward service/locust 8089:8089 -n locust`
6. Else you can use the locust APIs to start and monitor the test

start the test (host=www.ddd.com does not matter, it takes value from gateway CR)

    kubectl port-forward service/locust 8089:8089 -n locust &
    sleep 5
    curl -X POST   http://localhost:8089/swarm   -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8'   -d 'user_count=5&spawn_rate=1&host=www.ddd.com'
    sleep 2
    kill $(jobs -p | awk '{print $1}')
    sleep 10

monitor the test

    unset a
    unset b
    kubectl port-forward service/locust 8089:8089 -n locust &
    sleep 5
    
    a=$(curl -s -X GET http://localhost:8089/stats/requests | jq '.stats[1].current_rps')
    b=$(curl -s -X GET http://localhost:8089/stats/requests | jq '.stats[1].num_failures')
    echo "######################################################################################## rate: $a"
    echo "######################################################################################## failure: $b"
    kill $(jobs -p | awk '{print $1}')
    sleep 2
    
    unset a
    unset b

6. you can delete the locust pods or restart the locust deployments or delete the locust replicasets to stop the test. 
`kubectl delete rs --all -n locust`


