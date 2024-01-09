import sys
import urllib.parse
import allure
import pytest
import pytest_check
from hoverpy import capture, simulate
import requests
import time
import json
import pytest_check as check
sys.path.append(r"..")
from Mock.cloudmos import CloudMOS


@capture("cloudmos.db")
def capture_get():
    start = time.time()
    json_data = json.dumps({"imei": "866863041284971", "role": "mobile"})
    _time = requests.post(urllib.parse.urljoin(url, "gettoken"), data=json_data, headers=headers)
    print(_time.json())
    print("Time taken: %f" % (time.time() - start))


@simulate("cloudmos.db")
def simulated_get():
    json_data = json.dumps({"imei": "866863041284971", "role": "mobile"})
    print(requests.post(urllib.parse.urljoin(url, "gettoken"), data=json_data, headers=headers).text)


@simulate("cloudmos.db", delays=[("172.16.23.173", 3000, "GET"), ("172.16.23.173", 1000, "POST")])
def simulate_latency():
    json_data = json.dumps({"imei": "866863041284971", "role": "mobile"})
    start = time.time()
    print(requests.post(urllib.parse.urljoin(url, "gettoken"), data=json_data, headers=headers).text)
    print("Time taken: %f" % (time.time() - start))


@pytest_check.check_func
def test_gettoken(mocker):
    new_token = CloudMOS()
    mock_value = {'refreshToken':
                      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJyZW5ldyIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiI4NjY4NjMwNDEyODQ5NzEiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zaWQiOiI4NjY4NjMwNDEyODQ5NzEiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIxMC8xNC8yMDIyIDEwOjU4OjIwIEFNIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy91c2VyZGF0YSI6Im1vYmlsZSIsIm5iZiI6MTY2NTYyOTkwMCwiZXhwIjoxNjY1NzE2MzAwLCJpc3MiOiJEaW5nTGkuTU9TLkNsb3VkLjIwMjIiLCJhdWQiOiJEaW5nTGlDbGllbnRzIn0.CQ6z8d0IiA4rdT2CObCeF6kT50figuZge-eeexpgPFU', 'accessToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJtb2JpbGUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiODY2ODYzMDQxMjg0OTcxIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc2lkIjoiODY2ODYzMDQxMjg0OTcxIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9leHBpcmF0aW9uIjoiMTAvMTQvMjAyMiAxMDo1NzoyMCBBTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOiIiLCJuYmYiOjE2NjU2Mjk4NDAsImV4cCI6MTY2NTcxNjI0MCwiaXNzIjoiRGluZ0xpLk1PUy5DbG91ZC4yMDIyIiwiYXVkIjoiRGluZ0xpQ2xpZW50cyJ9.xZuURuMkQ4WFAlqDen_tkXPGkovdqdlowwfc1cY-DbQ', 'expiresIn': '2022-10-14T10:57:20.6651727+08:00', 'tokenType': 'Bearer'}
    with allure.step("Mock gettoken函数并返回值"):
        new_token.gettoken = mocker.patch.object(CloudMOS, "gettoken", return_value=mock_value)
    # new_token.gettoken = mocker.patch('cloudmos.Authentication.gettoken', return_value=mock_value)
    result = new_token.uploadfile()
    with allure.step("断言Mock 的gettoken函数是否被调用到"):
        CloudMOS.gettoken.assert_called_with()
    with check.check:
        with allure.step("断言upload返回的msg信息"):
            assert result.get('msg') == '上传成功！'


@pytest_check.check_func
def test_registerimei(mocker):
    new_test = CloudMOS()
    _result=new_test.registerIMEI('8668630412849719999999999999')
    with check.check:
        with allure.step("断言 registerimei 函数返回值是否正确"):
            assert _result == 'IMEI 位数不正确'


if __name__ == "__main__":
    # capture_get()
    # simulated_get()
    # simulate_latency()
    pytest.main(["-s"])
