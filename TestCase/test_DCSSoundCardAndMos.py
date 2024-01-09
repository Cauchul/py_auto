# -*- coding:utf-8 -*-
import hashlib
import time

import allure
import pytest
from pytest_check import check

from Common.GobalVariabies import *
from Common.Operation import *
from TestCase.GobalVariabies import *


class TestDCSSoundCardAndMos:
    def setup_class(self):
        # 拷贝算分需要的init文件到dcs目录下
        init_json_path = os.path.join(os.path.dirname(xml_path), 'initData.json')
        if os.path.exists(init_json_path):
            os.remove(init_json_path)
        copy_file(init_json_path, exe_path)

        # 新建Tmp目录
        tmp_dir = os.path.join(dcs_path, r'dcs_build\bin\Tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        with allure.step('获取可以使用的模块端口'):
            TestDCSSoundCardAndMos.device_id = get_device_id_from_redis()
            print('device_id: ', TestDCSSoundCardAndMos.device_id)

            dev_hash_name = get_all_run_process(TestDCSSoundCardAndMos.device_id)
            TestDCSSoundCardAndMos.test_port_list = check_module(dev_hash_name)

            with allure.step('期望值：值不为空，实际值：{0}'.format(TestDCSSoundCardAndMos.test_port_list)):
                print('TestDCSSoundCardAndMos.test_port_list: ', TestDCSSoundCardAndMos.test_port_list)
                assert TestDCSSoundCardAndMos.test_port_list

        with allure.step('连接UIService'):
            websocket_status = ui_service_project.connect()
            with check.check:
                with allure.step('断言 UIService 的连接状态是否为101. {0}'.format(websocket_status == 101)):
                    assert websocket_status == 101

    def teardown_class(self):
        ui_service_project.disconnect()

    @pytest.mark.skip(reason="跳过声卡mos测试，不能生成正常的录音文件")
    def test_sound_card_and_mos_service(self):
        update_test_plan(test_plan_id=4, device_id=TestDCSSoundCardAndMos.device_id)

        # 发送命令给数据集，开始采集数据
        with allure.step('发送StartWork命令: {0}'.format(ui_start_work_cmd)):
            print('发送StartWork命令 {0}'.format(ui_start_work_cmd))
            ui_send(ui_start_work_cmd, 0)
        print('发送StartWork命令')
        time.sleep(3)

        # 开始语音测试
        with allure.step('发送控制命令，启动语音业务'):
            with allure.step('发送更新测试计划命令: {0}'.format(ui_update_test_plan_cmd)):
                print('发送 UpdateTestplan 命令 {0}'.format(ui_update_test_plan_cmd))
                ui_send(ui_update_test_plan_cmd, 0)
            time.sleep(3)

            with allure.step('发送开始测试命令: {0}'.format(ui_start_test_cmd)):
                print('发送 StartTestPlan 命令 {0}'.format(ui_start_test_cmd))
                ui_send(ui_start_test_cmd, 8)
                ui_send(ui_start_test_cmd, 1)

            # 获取测试状态
            hash_key_1 = TestDCSSoundCardAndMos.device_id + '-DCSTestSchedule-1'
            hash_key_8 = TestDCSSoundCardAndMos.device_id + '-DCSTestSchedule-8'
            # 等待业务进行
            with allure.step('等待语音业务启动'):
                cnt = 0
                while True:
                    if cnt > 10:
                        with allure.step('语音业务启动超时'):
                            print('语音业务启动超时')
                            break
                    if 'Testing' == f_redis.hget(hash_key_1, 'test_status') == f_redis.hget(hash_key_8, 'test_status'):
                        with allure.step('语音业务开始测试'):
                            print('语音业务进行中......')
                            break
                    else:
                        cnt += 1
                        with allure.step('第 {0} 次检测，语音业务还未启动，等待 3s ......'.format(cnt)):
                            time.sleep(3)

            print('检测是否会产生新的录音文件')
            dir_path = os.path.join(dcs_path, r'dcs_build\bin\Tmp')
            last_files = set(os.listdir(dir_path))  # 获取初始化时文件夹中的所有文件列表

            with allure.step('等待 30s......, 查看是否产生新的录音文件'):
                print('等待 30s......, 查看是否产生新的录音文件')
                time.sleep(30)  # 等待 30s 查看是否产生新的录音文件
                new_files = set(os.listdir(dir_path))  # 获取当前文件夹中的所有文件列表
                diff_files = new_files - last_files  # 获取新增的文件列表
                with allure.step('新增文件为：{0}'.format(diff_files)):
                    print("新增文件：", diff_files)

            if diff_files:
                # with allure.step('Success, 新生成的录音文件为：{0}'.format(diff_files)):
                pass
            else:
                with check.check:
                    with allure.step('Fail, 未找到新生成的录音文件'):
                        assert diff_files

            file_md5_dict = {}
            with allure.step('获取录音文件的 md5 值'):
                # 获取新生成的文件的 md5 值
                if diff_files:
                    for file in diff_files:
                        md5 = hashlib.md5()
                        file_path = os.path.join(dir_path, file)
                        chunk_size = 1024 * 1024  # 每次读取1MB数据
                        with open(file_path, 'rb') as f:
                            while True:
                                data = f.read(chunk_size)
                                if not data:
                                    break
                                md5.update(data)
                        file_md5_dict[file] = md5.hexdigest()
                        with allure.step('文件 {0} 的MD5值：{1}'.format(file_path, md5.hexdigest())):
                            print("文件{}的MD5值：{}".format(file_path, md5.hexdigest()))

            print('等待 5s,获取mos分值')
            time.sleep(5)
            # 根据 md5 值获取分值
            for file_key in file_md5_dict:
                file_md5 = file_md5_dict[file_key]
                sql_get_mos_score = 'select "mos_file_def"."score" from "public"."mos_file_def" WHERE ' \
                                               '"mos_file_def"."md5" = \'{0}\''.format(file_md5)
                mos_score = pg_project.pg_run_sql_fetchone(sql_get_mos_score)[0]
                with check.check:
                    with allure.step('断言文件 mos 分值，算分文件为：{0}，期望分值：分值大于 3000 ，实际分值：{1}'.format(file_key, mos_score)):
                        print('文件{0}，的分值为：{1}'.format(file_key, mos_score))
                        assert 3000 < mos_score


if __name__ == "__main__":
    TestDCSSoundCardAndMos().setup_class()





