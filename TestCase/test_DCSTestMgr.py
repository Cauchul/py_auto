import subprocess
import time
import allure
import pytest
import pytest_check as check
import xml.etree.ElementTree as et
import sys
import websocket

from pytest_check import check_func
from Common.GobalVariabies import *
from Common.Operation import *

sys.path.append("..")


def get_pg_data_generate_xml(sql_cmd, xml_name, pg_column_name):
    pg_data = pg_project.pg_select_data(sql_cmd)
    if not pg_data.empty:
        with open(xml_name, 'w') as f_p:
            f_p.write(pg_data[pg_column_name][0])
            return True
    return False


def deal_test_plan_get_data(xml_data):
    res_data = {}
    total_count_dict = {}
    group_name = xml_data[0]['GroupName']
    for data in xml_data:
        if group_name != data['GroupName']:
            group_name = data['GroupName']
        if 'total_parallel_group_count' in data.keys():
            total_count = int(data['total_group_count']) * int(data['total_parallel_group_count'])
            if data['TaskName'] in res_data.keys():
                task_count = int(data['TaskRepeatCount']) * total_count + res_data[data['TaskName']]
            else:
                task_count = int(data['TaskRepeatCount']) * total_count
        else:
            total_count = int(data['total_group_count'])
            if data['TaskName'] in res_data.keys():
                task_count = int(data['TaskRepeatCount']) * total_count + res_data[data['TaskName']]
            else:
                task_count = int(data['TaskRepeatCount']) * total_count
        res_data[data['TaskName']] = task_count
        total_count_dict[group_name] = total_count
    return res_data, total_count_dict


def get_test_plan_xml_data(port):
    res_list = []
    xml_name = os.path.join(local_tmp_path, 'testplan_config_port_{0}_def_pg_data.xml'.format(port))
    if not os.path.exists(xml_name):
        with check.check:
            with allure.step('Failed, 端口 {0} 的测试计划xml文件 {1} 未找到'.format(port, xml_name)):
                assert os.path.exists(xml_name)
                return
    root = ParseXml.get_root_by_xml_name(xml_name)
    task_groups_node = ParseXml.get_root_by_element_name(root, 'TaskGroups')

    for group_config in task_groups_node:
        normal_tmp_dict = {}
        parallel_tmp_dict = {}
        group_config_data = ParseXml.parse_xml_data_to_dict_by_node(group_config)
        print('group_config_data: ', group_config_data)
        tasks_node = ParseXml.get_root_by_element_name(group_config, 'Tasks')
        for task_config in tasks_node:
            task_config_data = ParseXml.parse_xml_data_to_dict_by_node(task_config)
            print('task_config_data: ', task_config_data)

            if 'Parallel Service' != task_config_data['TaskType']:
                normal_tmp_dict['GroupName'] = group_config_data['GroupName']
                normal_tmp_dict['total_group_count'] = group_config_data['GroupRepeatCount']
                normal_tmp_dict['TaskName'] = task_config_data['TaskName']
                normal_tmp_dict['TaskRepeatCount'] = task_config_data['TaskRepeatCount']
                res_list.append(normal_tmp_dict)
                normal_tmp_dict = {}

            for node in task_config:
                if 'TaskType' == node.tag and 'Parallel Service' == node.text:  # 并行
                    task_list_node = ParseXml.get_root_by_element_name(task_config, 'TaskList')
                    for task in task_list_node:
                        task_data = ParseXml.parse_xml_data_to_dict_by_node(task)
                        print('task_data: ', task_data)
                        parallel_tmp_dict['GroupName'] = group_config_data['GroupName']
                        parallel_tmp_dict['total_group_count'] = group_config_data['GroupRepeatCount']
                        parallel_tmp_dict['parallel_group_TaskType'] = task_config_data['TaskType']
                        parallel_tmp_dict['total_parallel_group_count'] = task_config_data['TaskRepeatCount']
                        parallel_tmp_dict['TaskName'] = task_data['TaskName']
                        parallel_tmp_dict['TaskRepeatCount'] = task_data['TaskRepeatCount']
                        res_list.append(parallel_tmp_dict)
                        parallel_tmp_dict = {}
    print('--' * 50)
    print(res_list)
    print('--' * 50)
    return res_list


@allure.feature('测试管理服务测试')
class TestDCSTestMgrService:
    def setup_class(self):
        pubsub.subscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-DCSUISrv-cmdrequest')

        with allure.step('获取可以使用的模块端口'):
            TestDCSTestMgrService.device_id = get_device_id_from_redis()
            print('device_id: ', TestDCSTestMgrService.device_id)

            dev_hash_name = get_all_run_process(TestDCSTestMgrService.device_id)
            TestDCSTestMgrService.test_port_list = check_module(dev_hash_name)

            with allure.step('期望值：值不为空，实际值：{0}'.format(TestDCSTestMgrService.test_port_list)):
                print('TestDCSTestMgrService.test_port_list: ',  TestDCSTestMgrService.test_port_list)
                assert TestDCSTestMgrService.test_port_list

        with allure.step('连接UIService'):
            websocket_status = ui_service_project.connect()
            print('websocket_status: ', websocket_status)
            with check.check:
                with allure.step('断言 UIService 的连接状态是否为101. {0}'.format(websocket_status == 101)):
                    assert websocket_status == 101

        with allure.step('当前测试端口为：{0}'.format(TestDCSTestMgrService.test_port_list)):
            print('当前测试端口为：{0}'.format(TestDCSTestMgrService.test_port_list))
        with allure.step('运行sql，更新测试计划'):
            get_test_plan_cmd = 'select "test_plan_data"."test_plan_xml" from ' \
                                '"public"."test_plan_data" WHERE ' \
                                '"test_plan_data"."id" = 1'
            with allure.step('获取测试计划的sql为：{0}'.format(get_test_plan_cmd)):
                serial_test_plan_data = pg_project.pg_run_sql_fetchall(get_test_plan_cmd)
                print(serial_test_plan_data)
            # 写pg表
            pg_insert_cmd = 'INSERT INTO "public"."testplan_history" (unified_xml, dev_id) VALUES (\'{0}\', \'{1}\')'.format(
                serial_test_plan_data[0][0], TestDCSTestMgrService.device_id)
            with allure.step('插入测试计划到 testplan_history 表的sql为：{0}'.format(pg_insert_cmd)):
                pg_project.pg_insert_data(pg_insert_cmd)

    def teardown_class(self):
        ui_service_project.disconnect()
        pubsub.unsubscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-DCSUISrv-cmdrequest')

    @pytest.mark.skip(reason="跳过")
    @allure.step('测试管理服务测试')
    @check_func
    def test_ui_func_to_test_manager(self):
        with allure.step('当前测试端口为：{0}'.format(TestDCSTestMgrService.test_port_list)):
            print('当前测试端口为：{0}'.format(TestDCSTestMgrService.test_port_list))

        with allure.step('发送更新测试计划命令给测试管理服务'):
            for port in TestDCSTestMgrService.test_port_list:
                update_cmd = {"API": "UpdateTestplan",
                              "Params": {"Name": "", "TimeZone": "", "TestPlanXml": "", "Origin": 0,
                                         "TestPort": int(port),
                                         "RequestId": "", "IsTest": True}}
                with allure.step('发送update_testplan命令: {0}'.format(update_cmd)):
                    print('发送update_testplan命令 {0}'.format(update_cmd))
                    ui_service_project.send(json.dumps(update_cmd))
        time.sleep(5)
        with allure.step('对比初始测试计划和解析生成的的测试计划'):
            self.parse_xml(TestDCSTestMgrService.test_port_list, local_tmp_path)
        time.sleep(5)
        with allure.step('发送开始测试命令给测试管理服务'):
            for port in TestDCSTestMgrService.test_port_list:
                start_cmd = {"API": "StartTestPlan", "Params": {'TestPort': int(port), 'RequestId': '', 'FileName': '', 'IsFileCut': 0}}
                with allure.step('发送start_test命令: {0}'.format(start_cmd)):
                    print('发送start_test命令 {0}'.format(start_cmd))
                    ui_service_project.send(json.dumps(start_cmd))
        time.sleep(5)
        with allure.step('读取redis信息，判断各服务状态'):
            self.check_redis()
        with allure.step('发送停止测试命令给测试管理服务'):
            for port in TestDCSTestMgrService.test_port_list:
                stop_cmd = {"API": "StopTestPlan",
                                 "Params": {'TestPort': int(port), 'RequestId': '', 'FileName': '', 'IsFileCut': 0}}
                with allure.step('发送start_test命令: {0}'.format(stop_cmd)):
                    print('发送StopTest命令 {0}'.format(stop_cmd))
                    ui_service_project.send(json.dumps(stop_cmd))

    # @pytest.mark.skip(reason="跳过")
    @allure.step('测试管理服务测试')
    @check_func
    def test_make_package_to_test_manager(self):
        package_project = PackageUnpack(dll_path)
        redis_chanel = TestDCSTestMgrService.device_id + '-DCSTestMgr-cmdrequest'
        print('channel: ', redis_chanel)

        # 发送更新测试计划
        cmd_json_update_testplan = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-DCSUISrv',
                          'method': 'update_alltestplan',
                          'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDcs-10'}
        cmd_update_testplan_res = pub_json_cmd_to_redis_chanel(package_project, cmd_json_update_testplan, pubsub, redis_chanel)
        print('cmd_update_testplan_res: ', cmd_update_testplan_res)

        with allure.step('对比初始测试计划和解析生成的的测试计划'):
            self.parse_xml(TestDCSTestMgrService.test_port_list, local_tmp_path)

       # 发送开始测试命令
        cmd_json_start_test = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-DCSUISrv',
                                    'method': 'start_test',
                                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDcs-10',
                                    'test_port': 0, 'is_file_cut': 0, 'file_name': ''}
        cmd_start_test_res = pub_json_cmd_to_redis_chanel(package_project, cmd_json_start_test, pubsub, redis_chanel)
        print('cmd_start_test_res: ', cmd_start_test_res)

        time.sleep(2)

        with allure.step('读取redis信息，判断各服务状态'):
            self.check_redis()

        # 发送停止测试命令
        cmd_json_stop_test = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-DCSUISrv',
                               'method': 'stop_test',
                               'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDcs-10',
                               'test_port': 0, 'is_file_cut': 0, 'file_name': ''}
        cmd_stop_test_res = pub_json_cmd_to_redis_chanel(package_project, cmd_json_stop_test, pubsub,
                                                          redis_chanel)
        print('cmd_stop_test_res: ', cmd_stop_test_res)


    @check_func
    def parse_xml(self, test_port_list, xml_path):
        # 读取所有测试计划，生成文件
        xml_name_testplan_history = os.path.join(xml_path, 'testplan_history_pg_data.xml')
        sql_cmd_select_testplan_history = 'select "testplan_history"."unified_xml" from "public"."testplan_history" ORDER BY "testplan_history"."id" DESC LIMIT 1'
        with check.check:
            with allure.step('生成文件：{0}'.format(xml_name_testplan_history)):
                assert get_pg_data_generate_xml(sql_cmd_select_testplan_history, xml_name_testplan_history, 'unified_xml')

        tree_root_testplan_history = ParseXml.get_root_by_xml_name(xml_name_testplan_history)
        print('tree_root_testplan_history: ', tree_root_testplan_history)
        # 用来保存xml解析结果的字典
        all_str = {}
        part_str = {}

        out_flag = True
        print('test_port_list: ', test_port_list)

        for port in test_port_list:
            print('cur_port: ', port)
            # 根据端口构建sql命令
            sql_cmd_testplan_config_port_def = 'select "testplan_config_port_def"."testschemas" from "public"."testplan_config_port_def" WHERE "testplan_config_port_def"."port" = {0}'.format(
                port)
            # 根据端口构建xml文件名称
            port_xml_name_testplan_config_port_def = os.path.join(xml_path, 'testplan_config_port_{0}_def_pg_data.xml'.format(port))
            with check.check:
                with allure.step('生成文件：{0}'.format(port_xml_name_testplan_config_port_def)):
                    assert get_pg_data_generate_xml(sql_cmd_testplan_config_port_def, port_xml_name_testplan_config_port_def, 'testschemas')


            # 获取端口的xml的根节点
            tree_root_testplan_config_port_def = ParseXml.get_root_by_xml_name(port_xml_name_testplan_config_port_def)

            # 解析端口xml内容到字典中
            for neighbor in tree_root_testplan_config_port_def.iter():
                part_str[neighbor.tag] = [(str(neighbor.attrib))]
                part_str[neighbor.tag].append((str(neighbor.text)))

            # 解析整测试计划xml内容到字典中
            node_test_schemas = tree_root_testplan_history.find('TestSchemas')
            for node_config in node_test_schemas:
                for node in node_config:
                    if 'PortNumber' == node.tag and int(port) == int(node.text):
                        for sub_node in node_config.iter():
                            all_str[sub_node.tag] = [(str(sub_node.attrib))]
                            all_str[sub_node.tag].append((str(sub_node.text)))

            # 清除两个字典中的回车和换行符
            if all_str:
                for i in all_str:
                    all_str[i][1] = all_str[i][1].strip()
                with allure.step('端口 {0} 原始测试计划： {1}'.format(port, all_str)):
                    print(all_str)

            if part_str:
                for i in part_str:
                    part_str[i][1] = part_str[i][1].strip()
                # 解析结果输出
                with allure.step('端口 {0} 解析后的测试计划： {1}'.format(port, part_str)):
                    print(part_str)

            flag = True
            # check result
            for i in all_str:
                if all_str[i] != part_str[i]:
                    with check.check:
                        with allure.step('Failed, 解析前后内容不一致，期望值：{0}，实际值：{1}，错误元素名：{2}'.format(all_str[i], part_str[i], i)):
                            flag = False
                            assert flag

            with check.check:
                if 'TaskIndex' in part_str:
                    pass
                else:
                    with allure.step("port {0} 的测试计划存在TaskIndex， 值为 {1}".format(port, part_str['TaskIndex'][1])):
                        out_flag = False
                        assert 'TaskIndex' in part_str
                if flag:
                    pass
                else:
                    with allure.step('port {0} 测试计划解析前后，各元素对比'.format(port)):
                        out_flag = False
                        assert flag
        if out_flag:
            with allure.step('success, 测试计划解析前后内容一致，解析成功'):
                pass

    @check_func
    def check_redis(self):
        for i_port in TestDCSTestMgrService.test_port_list:
            with allure.step('检查端口：{0}'.format(i_port)):
                hash_name = TestDCSTestMgrService.device_id + '-DCSTestSchedule-{0}'.format(i_port)
                print('hash_name: ', hash_name)
                test_info = f_redis.hgetall(hash_name)
                print('test_info: ', test_info)

                with allure.step('hash_name:{0}'.format(hash_name)):
                    test_status = test_info['test_status']
                    with check.check:
                        with allure.step('断言,test_status，期望值：Testing，实际值：{0}'.format(test_status)):
                            assert 'Testing' == test_status

                    total_group_count = test_info['total_group_count']
                    total_parallel_group_count = test_info['total_parallel_group_count']

                    if total_group_count and total_parallel_group_count:
                        total_count = int(total_group_count) * int(total_parallel_group_count)

                    print('total_count: ', total_count)

                    xml_data = get_test_plan_xml_data(i_port)
                    task_circulation_total_count_dict, external_circulation_total_count_dict = deal_test_plan_get_data(
                        xml_data)
                    actual_total_count = external_circulation_total_count_dict[
                        list(external_circulation_total_count_dict.keys())[0]]
                    print('actual_total_count：', actual_total_count)
                    with check.check:
                        with allure.step('断言外循环次数, 期望值：{0} 实即值：{1}'.format(total_count, actual_total_count)):
                            assert total_count == actual_total_count


if __name__ == "__main__":
    new_test = TestDCSTestMgrService()
    new_test.get_test_status_from_redis()
    # 运行sql脚本插入数据
    # new_test.run_sql_scripte_add_data_to_pg('')
    # new_test.test_updatetestplan()
    # new_test.run_sql_scripte_add_data_to_pg(r'E:\port_def_8_port.sql')
    # new_test.run_sql_scripte_add_data_to_pg(r'E:\testplan_history_8_port.sql')
    # new_test.start_service()
    # new_test.send_start_cmd()
    # time.sleep(2)
    # new_test.parse_xml()
    # time.sleep(5)
    # new_test.send_UpdateTestPlan_cmd_func()
