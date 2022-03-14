import socket
import requests
from kubernetes import client
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def override_dns():
    prv_getaddrinfo = socket.getaddrinfo
    dns_cache = {}

    def new_getaddrinfo(*args):
        if args[0] in dns_cache:
            logger.info("Forcing FQDN: %s to IP: %s", args[0], dns_cache[args[0]])
            return prv_getaddrinfo(dns_cache[args[0]], *args[1:])
        else:
            return prv_getaddrinfo(*args)

    socket.getaddrinfo = new_getaddrinfo
    return dns_cache


def test_services_are_reachable(override_dns):
    kube_client = client.CoreV1Api()
    svc = kube_client.read_namespaced_service(
        name="istio-ingressgateway", namespace="istio-system"
    )
    ip = svc.status.load_balancer.ingress[0].ip
    virtual_svcs = client.CustomObjectsApi().list_cluster_custom_object(
        group="networking.istio.io", version="v1beta1", plural="virtualservices"
    )
    domains = [vs["spec"]["hosts"][0] for vs in virtual_svcs["items"]]

    failed_vs = []
    for domain in domains:
        override_dns[domain] = ip
        resp = requests.get(f"https://{domain}", verify=False)
        if resp.status_code != 200:
            failed_vs.append((domain, resp.status_code))

    assert (
        len(failed_vs) == 0
    ), f"Unexpected status code from virtual services {failed_vs}"
