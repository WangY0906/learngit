# coding: utf-8
import tornado.web
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from util.ApiConfiger import ApiConfig
import json
import traceback
import logging
import uuid
import time

class post_Handler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print('GET')
        logging.info('GET stub')
        self.finish()

    def parse(self, data):
        return json.loads(data.decode('utf-8'))

    def genV1Pod(self, uid, workType, seq, count, info, ps, workers):
        tfId = "-".join(["tf", str(uid), workType, str(seq), str(count)])

        body = kubernetes.client.V1Pod()  # V1Pod |
        body.api_version = "v1"
        body.kind = "Pod"
        body.metadata = kubernetes.client.V1ObjectMeta()
        body.metadata.name = tfId
        body.metadata.labels = {"tf": tfId}

        containerBody = kubernetes.client.V1Container(name=tfId)
        containerBody.image = "nginx"
        portBody = kubernetes.client.V1ContainerPort(container_port=2222)
        containerBody.ports = [portBody]

        body.spec = kubernetes.client.V1PodSpec(containers=[containerBody])
        return body

    def createPod(self, uid, info):
        config.load_kube_config(r'C:\Users\Administrator\Desktop\distributed-tensorflow-master_2\conf\lv\config')
        configuration = kubernetes.client.Configuration()
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        namespace = 'default'
        runInfo = info.get("detail", None)
        ps_count = runInfo.get("ps", 0)
        worker_count = runInfo.get("worker", 0)
        svcPort = ApiConfig().get("k8s", "headless_port")
        ps_hosts = ["-".join(["tf", str(uid), "ps", str(i), str(ps_count)]) + ":" + svcPort for i in range(ps_count)]
        worker_hosts = ["-".join(["tf", str(uid), "worker", str(i), str(worker_count)]) + ":" + svcPort for i in range(worker_count)]
        for workType in runInfo:
            count = runInfo.get(workType, 1)
            for i in range(count):
                try:
                    body = self.genV1Pod(uid, workType, i, count, info, ",".join(ps_hosts), ",".join(worker_hosts))
                    print (body)
                    namespace = ApiConfig().get("namespace", info.get("type", "tensorflow"))
                    api_response = api_instance.create_namespaced_pod(namespace, body)
                    print (api_response)
                    logging.info("create pod: " + str(api_response))
                except ApiException as e:
                    print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
                    logging.info("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
                    raise
        return ps_hosts, worker_hosts

    def submit(self, info):
        uid = uuid.uuid1()
        ps_hosts, worker_hosts = self.createPod(uid, info)
        tf_hosts = ps_hosts + worker_hosts
        self.write(json.dumps([pod.split(":")[0] for pod in tf_hosts]))


    @tornado.web.asynchronous
    def post(self):
        try:
            print("POST")
            print("data: " + str(self.request.body))
            logging.info("POST data: " + str(self.request.body))

            info = self.parse(self.request.body)
            print("parse data: " + str(info))
            logging.info("parse data: " + str(info))
            self.submit(info)
            time.sleep(20)

            name = "tf-f3184f28-02a9-11e9-ae74-54ee759117a8-worker-1-2"
            namespace = "default"
            config.load_kube_config(r'D:/python/project/test/distributed-tensorflow-master_2/conf/lenovo/config')
            configuration = kubernetes.client.Configuration()
            api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
            try:
                api_response = api_instance.read_namespaced_pod(name, namespace)
                self.write(api_response.status.pod_ip)
            except ApiException as e:
                print("Exception when calling CoreV1Api->read_namespaced_pod: %s\n" % e)


            self.finish()
        except:
            traceback.print_exc()

