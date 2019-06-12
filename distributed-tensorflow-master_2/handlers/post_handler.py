# coding: utf-8
from pprint import pprint
import tornado
import tornado.web
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
from util.ApiConfiger import ApiConfig
from util.RedisHelper import RedisHelper
import logging
import traceback
import uuid

class PostHandler(tornado.web.RequestHandler):
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
        containerBody.image = "tensorflow/tensorflow"
        portBody = kubernetes.client.V1ContainerPort(container_port=2222)
        containerBody.ports = [portBody]
        body.spec = kubernetes.client.V1PodSpec(containers=[containerBody])

        return body

    def createPod(self, uid, info):
        # Configure API key authorization: BearerToken
        config.load_kube_config(r'C:\Users\Administrator\Desktop\distributed-tensorflow-master_2\conf\lv\config')
        configuration = kubernetes.client.Configuration()
        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['authorization'] = 'Bearer'

        # create an instance of the API class
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        runInfo = info.get("detail", None)
        ps_count = runInfo.get("ps", 0)
        worker_count = runInfo.get("worker", 0)
        svcPort = ApiConfig().get("k8s", "headless_port")
        ps_hosts = ["-".join(["tf", str(uid), "ps", str(i), str(ps_count)]) + ":" + svcPort for i in range(ps_count)]
        worker_hosts = ["-".join(["tf", str(uid), "worker", str(i), str(worker_count)]) + ":" + svcPort for i in
                        range(worker_count)]
        print("ps: " + str(ps_hosts))
        logging.info("ps: " + str(ps_hosts))
        print("worker: " + str(worker_hosts))
        logging.info("worker: " + str(worker_hosts))
        for workType in runInfo:
            count = runInfo.get(workType, 1)
            for i in range(count):
                try:
                    body = self.genV1Pod(uid, workType, i, count, info, ",".join(ps_hosts), ",".join(worker_hosts))
                    print(body)
                    namespace = ApiConfig().get("namespace", info.get("type", "tensorflow"))
                    api_response = api_instance.create_namespaced_pod(namespace, body)
                    print(api_response)
                    logging.info("create pod: " + str(api_response))
                except ApiException as e:
                    print("Exception when calling BatchV1Api->create_namespaced_pod: %s\n" % e)
                    logging.info("Exception when calling BatchV1Api->create_namespaced_pod: %s\n" % e)
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
            para = json.loads(self.request.body)
            logging.info("POST data: " + str(self.request.body))
            info = self.parse(self.request.body)
            print("parse data: " + str(info))
            logging.info("parse data: " + str(info))
            print("detail" + str(para["detail"]))
            self.write('ok')
            self.submit(info)
            self.finish()
        except:
            traceback.print_exc()