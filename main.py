from locust import HttpUser, task, between, constant_throughput
from unittest.mock import patch
import time


import requests
from lib.locust_lib import get_gw_hosts_list, get_first_node_internal_ip, get_node_port, get_lb_ip

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}


class WebsiteUser(HttpUser):

    node_ip = get_first_node_internal_ip()
    node_port = get_node_port("istio-system", "app=istio-ingressgateway")
    lb_ip = get_lb_ip("istio-system", "app=istio-ingressgateway")
    host_list = get_gw_hosts_list("istio-system", "gw=bookinfo-gateway")


    def connect_to(self, host, port):
        from urllib3.util.connection import create_connection as orig_create_connection

        def _forced_address_connection(address, *args, **kwargs):
            forced_address = (host, port)
            return orig_create_connection(forced_address, *args, **kwargs)

        return patch('urllib3.util.connection.create_connection', _forced_address_connection)


    @task(1)
    def get_product_page(self):
        session = requests.Session()

        for host in self.host_list :
            url = "https://"+host+"/productpage"
            print(url)
            self.client.verify = False
            with self.connect_to(self.node_ip, self.node_port) :
                self.client.get(url, headers=default_headers)
                time.sleep(0.1)
        session.close()
