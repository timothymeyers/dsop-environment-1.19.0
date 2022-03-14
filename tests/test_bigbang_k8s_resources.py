from kubernetes import client


def test_namespaces_created():
    expected_ns = {
        "bigbang",
        "default",
        "eck-operator",
        "flux-system",
        "gatekeeper-system",
        "istio-operator",
        "istio-system",
        "jaeger",
        "kiali",
        "kube-node-lease",
        "kube-public",
        "kube-system",
        "logging",
        "monitoring",
        "twistlock",
    }

    ns_details = client.CoreV1Api().list_namespace()
    actual_ns = {detail.metadata.name for detail in ns_details.items}
    missing_ns = expected_ns - actual_ns

    assert len(missing_ns) == 0, f"Missing namespaces {missing_ns}"


def test_successful_pod_status():
    expected_status = ["Succeeded", "Running"]

    pods = client.CoreV1Api().list_pod_for_all_namespaces().items
    failed_pods = [
        (pod.metadata.name, pod.status.phase)
        for pod in pods
        if pod.status.phase not in expected_status
    ]

    assert len(failed_pods) == 0, f"Unexpected pod phase {failed_pods}"


def test_successful_deployment_status():
    kube_client = client.AppsV1Api()
    deployments = kube_client.list_deployment_for_all_namespaces()

    failed_deployments = {
        (d.metadata.name, d.status.unavailable_replicas)
        for d in deployments.items
        if d.status.unavailable_replicas is not None
        and d.status.unavailable_replicas > 0
    }

    assert (
        len(failed_deployments) == 0
    ), f"Deployments with unavailable replicas {failed_deployments}"


def test_virtual_services_deployed():
    expected_vs = [
        "tracing",  # jaeger
        "kiali",
        "kibana",
        "grafana",
        "prometheus",
        "twistlock",
    ]

    virtual_svcs = client.CustomObjectsApi().list_cluster_custom_object(
        group="networking.istio.io", version="v1beta1", plural="virtualservices"
    )
    domains = [vs["spec"]["hosts"][0] for vs in virtual_svcs["items"]]
    actual_vs = [d.split(".")[0] for d in domains]

    missing_vs = [vs for vs in expected_vs if vs not in actual_vs]

    assert len(missing_vs) == 0, f"Missing virtual services {missing_vs}"
