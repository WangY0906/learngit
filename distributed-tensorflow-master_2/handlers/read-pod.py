from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from kubernetes import client, config

name = "nginx"
namespace = "default"
config.load_kube_config(r'C:\Users\Administrator\Desktop\distributed-tensorflow-master_2\conf\lv\config')
configuration = kubernetes.client.Configuration()
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['authorization'] = 'Bearer'

# create an instance of the API class
api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
try:
    api_response = api_instance.read_namespaced_pod(name , namespace)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CoreV1Api->read_namespaced_pod: %s\n" % e)

print("pod_ip:"+api_response.status.pod_ip)