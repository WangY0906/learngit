from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from kubernetes import client, config

# Configure API key authorization: BearerToken
config.load_kube_config(r'C:\Users\Administrator\Desktop\distributed-tensorflow-master_2\conf\lv\config')
configuration = kubernetes.client.Configuration()
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['authorization'] = 'Bearer'

# create an instance of the API class
api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
name = "nginx"
namespace = 'default' # str | object name and auth scope, such as for teams and projects
body = kubernetes.client.V1Pod() # V1Pod |
body.api_version = "v1"
body.kind = "Pod"
body.metadata = kubernetes.client.V1ObjectMeta()
body.metadata.name = "nginx"
body.metadata.labels = {"app": "nginx"}

containerBody = kubernetes.client.V1Container(name="nginx")
containerBody.image = "nginx"
portBody = kubernetes.client.V1ContainerPort(container_port=2222)
containerBody.ports = [portBody]

body.spec = kubernetes.client.V1PodSpec(containers=[containerBody])

try:
    api_response = api_instance.create_namespaced_pod(namespace, body)

except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)


try:
    api_response = api_instance.read_namespaced_pod(name , namespace)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CoreV1Api->read_namespaced_pod: %s\n" % e)