from platform import node
from kubernetes import client, config
import json
import subprocess

def get_first_node_internal_ip() :

    # fetches the internal IP of first node in the cluster

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()

    first_node=apps_v1.list_node().items[0].status.addresses

    for addr in first_node :
        if addr.type == "InternalIP" :
            first_node_internal_ip = addr.address
    
    return(first_node_internal_ip)


def get_gw_hosts_list(ns,label):

    # fetches hosts defined in GW given with label selectors and namespace

    #get ns if locust is run in same namespace as the GW - not needed here
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    #config.load_kube_config()
    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()
    custom_v1 = client.CustomObjectsApi()

    host_list = []

    gw_crd = custom_v1.list_namespaced_custom_object(
        group="networking.istio.io", version="v1beta1", plural="gateways", namespace=ns, label_selector=label)

    for gw in gw_crd['items']:

        host_array = gw['spec']['servers'][0]['hosts']

        for host in host_array:
            host1 = host.split("/")[1]
            host_list.append(host1)

    return(host_list)
    

def get_node_port(ns, svcname) :

    # fetches node port a GW service in given namespace.

    # get ns if locust is run in same namespace as the GW - not needed here
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()

    node_port = ""

    service  = apps_v1.read_namespaced_service(svcname,ns)
    svc_ports = service.spec.ports

    for x in svc_ports:
        if x.port == 443:
            node_port = str(x.node_port)

    return(node_port)


def get_lb_ip(ns, svcname) :

    # fetches LB IP of a GW service in given namespace.

    # get ns if locust is run in same namespace as the GW - not needed here
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()

    lb_ip = ""

    service  = apps_v1.read_namespaced_service(svcname,ns)
    lb_ip = service.status.load_balancer.ingress[0].ip

    return(lb_ip)

def get_cluster_ip(ns, svcname) :

    # fetches cluster IP of a GW service in given namespace.

    # get ns if locust is run in same namespace as the GW - not needed here
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()

    cluster_ip = ""

    service  = apps_v1.read_namespaced_service(svcname,ns)
    cluster_ip = str(service.spec.cluster_ip)

    return(cluster_ip)
