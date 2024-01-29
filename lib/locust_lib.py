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

    #get ns if locust is run in same namespace as the GW
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
    

def get_node_port(ns,label) :

    # fetches node port a GW service in given namespace.

    # get ns if locust is run in same namespace as the GW
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()
    custom_v1 = client.CustomObjectsApi()

    node_port = ""

    
    gw_crd = custom_v1.list_namespaced_custom_object(
        group="networking.istio.io", version="v1beta1", plural="gateways", namespace=ns, label_selector=label)
    
    for gw in gw_crd['items']:
        gw_name = gw['spec']['selector']['app']
        service_names = apps_v1.read_namespaced_service(gw_name, ns).spec.ports

        for svc in service_names:
            if svc.port == 443:
                node_port = str(svc.node_port)


    return(node_port)

def get_lb_ip(ns, label) :

    # fetches LB IP of a GW service in given namespace.

    # get ns if locust is run in same namespace as the GW
    #ns = subprocess.run(["cat", "/var/run/secrets/kubernetes.io/serviceaccount/namespace"], stdout=subprocess.PIPE).stdout.decode('utf-8')

    config.load_incluster_config()
    apps_v1 = client.CoreV1Api()
    custom_v1 = client.CustomObjectsApi()

    lb_ip = ""

    return(lb_ip)