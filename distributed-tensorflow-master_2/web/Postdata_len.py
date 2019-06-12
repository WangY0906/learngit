import http.client

conn = http.client.HTTPConnection("localhost:12345")

payload = "{\r\n    \"type\": \"tensorflow\",\r\n    \"file\": \"/tmp/mnist.tgz\",\r\n    \"data\": \"notebooks/MNIST_data\",\r\n    \"resource\": {\r\n        \"cpu\": 2,\r\n        \"mem\": \"4g\",\r\n        \"gpu\": 1\r\n    },\r\n    \"detail\": {\r\n        \"ps\": 1,\r\n        \"worker\": 2\r\n    }\r\n}\r\n"

headers = {
    'cache-control': "no-cache",
    'postman-token': "0fca0b89-2b33-4212-b47f-e16e9855f64f"
    }

conn.request("POST", "/v1/train", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))