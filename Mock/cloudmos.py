import json
import requests
from urllib import parse
import time

url = "http://172.16.23.173"
headers = {'User-Agent': 'Python win32 2.10', 'content-type': 'application/json'}


class CloudMOS(object):
    def __init__(self):
        pass

    @classmethod
    def registerIMEI(cls, imei):
        start = time.time()
        json_data = json.dumps({"imei": imei, "desc": "mobile"})
        _result = requests.post(parse.urljoin(url, "register-imei"), data=json_data, headers=headers)
        print(_result.json())
        print("Time taken: %f" % (time.time() - start))
        return _result.json()

    def getToken(self):
        pass

    def uploadFile(self):
        token=self.getToken()
        if json.dumps(token)[1] != '2022-10-14T10:57:20.6651727+08:00':
            return {"status": 0, "msg": "上传成功！"}
        else:
            return {"status": 1, "msg": "上传失败！"}
