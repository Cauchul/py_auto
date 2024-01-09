import ctypes
from ctypes import *
import os
import pytest
import sys
import json
sys.path.append("..")
from Common.Operation import *


class TestDaemonService:
    def test_stopservice(self):
        cmd_json = '{cmd:"stop", from:"PFS-979FBB808A58C936E07235A71B9C728B-CN.GuangDong.Zhuhai-DCSTestMgr", server_name:"DCSTestMgr", test_port:"-1"}'
        redis_chanel = 'PFS-979FBB808A58C936E07235A71B9C728B-CN.GuangDong.Zhuhai-DCSDaemon-cmdrequest'

        new_redis = RedisOperations(host='172.16.23.142')
        new_redis.connect()
        print(len(cmd_json))
        packed_json = MakePackageAndUnpackage().makepackage(cmd_json)
        print(packed_json)
        new_redis.pub(redis_chanel, packed_json)
        MakePackageAndUnpackage().uninit_handle()


if __name__ == "__main__":
    new_test = TestDaemonService()
    new_test.test_stopservice()





