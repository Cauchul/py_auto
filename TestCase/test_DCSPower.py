# -*- coding:utf-8 -*-
import time

import allure
import pytest
import serial.tools.list_ports

from pytest_check import check

from Common.GobalVariabies import *


def get_power_path_from_pg(port):
    sql_cmd = 'select "port_def"."power_path" from "public"."port_def" WHERE ' \
              '"port_def"."port" = {0}'.format(port)
    print('sql_cmd: ', sql_cmd)
    res_power_path = TestDCSPower.local_pg.pg_run_sql_fetchone(sql_cmd)
    print('当前测试端口：', port)
    print('power_path: ', res_power_path)
    if res_power_path:
        return res_power_path[0]
    return False


# 测试修改上下电模式功能
def get_power_mode_from_pg(port):
    sql_cmd = 'select "port_def"."power_mode" from "public"."port_def" WHERE ' \
              '"port_def"."port" = {0}'.format(port)
    print('sql_cmd: ', sql_cmd)
    res_power_mode = TestDCSPower.local_pg.pg_run_sql_fetchone(sql_cmd)
    print('res_power_mode: ', res_power_mode)
    if res_power_mode:
        return res_power_mode[0]
    return False


# 设置上下电模式
def set_port_mode(hw_port='module_0', port_mode='level'):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'set_port_mode',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': 0, 'hw_port': hw_port, 'port_mode': port_mode}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPower.package_project, cmd_json, pubsub, TestDCSPower.dcs_power_chanel)
    print('cmd_res: ', cmd_res)


def set_port_power(port, port_power, hw_port=None):
    if hw_port is None:
        hw_port = get_power_path_from_pg(port)
    print('hw_port: ', hw_port)
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'set_port_power',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': port, 'hw_port': hw_port, 'port_power': port_power}

    with allure.step('发送的命令为：{0}'.format(cmd_json)):
        pass

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPower.package_project, cmd_json, pubsub, TestDCSPower.dcs_power_chanel)
    with allure.step('命令的返回值为：{0}'.format(cmd_res)):
        print('cmd_res: ', cmd_res)
    return cmd_res


def power_on(on_port):
    res = set_port_power(on_port, 'on')
    if res:
        if res['result']:
            with allure.step('成功，上电命令发送成功'):
                print('成功，上电命令发送成功')
        else:
            with check.check:
                with allure.step('失败，上电命令返回值为：{0}'.format(res['result'])):
                    print('失败，上电命令返回值为：{0}'.format(res['result']))
                    assert res['result']
    else:
        with check.check:
            with allure.step('失败，上电命令返回值为：{0}'.format(res)):
                print('失败，上电命令返回值为：{0}'.format(res))
                assert res


def power_on_send_hw_port(on_port, hw_port):
    res = set_port_power(on_port, 'on', hw_port)
    if res:
        return res
    else:
        with check.check:
            with allure.step('命令返回失败，期望值：返回值不为空，实际值：{0}'.format(res)):
                assert res


def power_off_send_hw_port(off_port, hw_port):
    res = set_port_power(off_port, 'off', hw_port)
    if res:
        return res
    else:
        with check.check:
            with allure.step('命令返回失败，期望值：返回值不为空，实际值：{0}'.format(res)):
                assert res


def power_off(off_port):
    res = set_port_power(off_port, 'off')
    if res:
        if res['result']:
            with allure.step('成功，下电命令发送成功'):
                print('成功，下电命令发送成功')
        else:
            with check.check:
                with allure.step('失败，下电命令返回值为：{0}'.format(res['result'])):
                    print('失败，下电命令返回值为：{0}'.format(res['result']))
                    assert res['result']
    else:
        with check.check:
            with allure.step('失败，下电命令返回值为：{0}'.format(res)):
                print('失败，下电命令返回值为：{0}'.format(res))
                assert res


def power_reset(reset_port):
    set_port_power(reset_port, 'reset')


def get_module_status(redis_hash_name):
    with allure.step('从 {0} 中获取模块状态'.format(redis_hash_name)):
        return f_redis.hget(redis_hash_name, 'module_status')


def get_usb_dev_info():
    tmp_dict = {}
    check_list = []
    pid_list = [0x0104, 0x9001, 0x010B, 0x0801]

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description:
            if port.serial_number not in check_list and port.pid in pid_list:
                check_list.append(port.serial_number)
                pid = hex(port.pid)
                vid = hex(port.vid)
                sn = port.serial_number
                tmp_dict[port.serial_number] = {'pid': pid, 'vid': vid}
                # tmp_dict[port.serial_number] = {'pid': pid, 'vid': vid, 'serial_number': sn}
                print("PID: {}, VID: {}, Serial Number: {}".format(pid, vid, sn))

    return tmp_dict


def get_two_dict_diff_key(dict1, dict2):
    return list(set(dict1.keys()) - set(dict2.keys()))


def get_pid_vid_from_pg():
    sql_cmd = 'select "module_def"."pid","module_def"."vid" from "public"."module_def"'
    pg_res_data = TestDCSPower.local_pg.pg_run_sql_fetchall(sql_cmd)
    pid_list = ['0x' + p_v[0].lower() for p_v in pg_res_data]
    vid_list = ['0x' + p_v[1].lower() for p_v in pg_res_data]
    return pid_list, vid_list


@allure.feature("电源服务测试用例")
class TestDCSPower:
    def setup_class(self):
        TestDCSPower.package_project = PackageUnpack(dll_path)
        pubsub.subscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

        TestDCSPower.local_pg = PostgresOperations(host='172.16.21.65', user='postgres', pwd='123456', db='postgres')  #dcsdb
        TestDCSPower.local_pg.pg_connect()

        with allure.step('获取电源服务通信 redis chanel'):
            TestDCSPower.device_id = get_device_id_from_redis()
            TestDCSPower.dcs_power_chanel = TestDCSPower.device_id + '-DCSPower-cmdrequest'
            with allure.step('电源服务redis chanel为：{0}'.format(TestDCSPower.dcs_power_chanel)):
                print('dcs_power_chanel: ', TestDCSPower.dcs_power_chanel)

        with allure.step('获取可用模块的端口'):
            port_list = get_can_use_module_port(TestDCSPower.device_id)
            if not port_list:
                with check.check:
                    with allure.step('当前可用端口为：{0}'.format(port_list)):
                        # assert port_list
                        print('test_list: ', port_list)

        with allure.step('从pg数据库中获取当前支持模块的所有pid list和vid list'):
            TestDCSPower.pid_list, TestDCSPower.vid_list = get_pid_vid_from_pg()
            with allure.step('获取到的pid list为：{0}，获取到的vid list为：{1}'.format(TestDCSPower.pid_list, TestDCSPower.vid_list)):
                print('pid_list: ', TestDCSPower.pid_list)
                print('vid_list: ', TestDCSPower.vid_list)

    def teardown_class(self):
        TestDCSPower.local_pg.pg_close()
        pubsub.unsubscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

    @pytest.mark.skip(reason="跳过下电测试，移远模块不支持")
    @allure.step('电源服务下电测试')
    @pytest.mark.parametrize("power_off_port", [1])
    def test_power_down(self, power_off_port):
        with allure.step('当前下电端口：{0}'.format(power_off_port)):
            # power_off_port = TestDCSPower.power_check_port
            print('power_off_port: ', power_off_port)
            redis_hash = TestDCSPower.device_id + '-DCSDeviceServer-{0}'.format(power_off_port)
            with allure.step('当前端口:{0}的redis_hash_name为：{1}'.format(power_off_port, redis_hash)):
                print('power_on_redis_hash: ', redis_hash)
        with allure.step('获取当前设备，所有usb设备的pid、vid和serial_number'):
            all_usb_dev_info = get_usb_dev_info()
            with allure.step('获取到的设备信息为：{0}'.format(all_usb_dev_info)):
                print('total_usb_dev_info: ', all_usb_dev_info)
        with allure.step('下电测试'):
            with allure.step('发送下电命令，并等待 6s'):
                power_off(power_off_port)
                print('等待 6s, 等待下电成功')
                time.sleep(6)
            with allure.step('检查设备pid、vid，判断设备是否下电成功'):
                power_off_usb_dev_info = get_usb_dev_info()
                with allure.step(
                        '下电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_off_usb_dev_info)):
                    print('power_off_usb_dev_info: ', power_off_usb_dev_info)
                two_dict_diff_key = get_two_dict_diff_key(all_usb_dev_info, power_off_usb_dev_info)
                if not two_dict_diff_key:
                    with check.check:
                        with allure.step('错误，获取下电设备序列号失败，期望值：值不空，实际值：{0}'.format(two_dict_diff_key)):
                            assert two_dict_diff_key
                else:
                    power_off_serial_number = two_dict_diff_key[0]
                    with allure.step('下电设备的序列号为：{0}，pid、vid为：{1}'.format(power_off_serial_number, all_usb_dev_info[power_off_serial_number])):
                        print('serial_number：{0}，pid_and_vid：{1}'.format(power_off_serial_number, all_usb_dev_info[power_off_serial_number]))
                    with allure.step(
                            '断言下电模块的pid，期望值：值存在pid list {0} 中，实际值：{1}'.format(TestDCSPower.pid_list, all_usb_dev_info[power_off_serial_number]['pid'].lower())):
                        assert all_usb_dev_info[power_off_serial_number]['pid'].lower() in TestDCSPower.pid_list
                    with allure.step(
                            '断言下电模块的vid，期望值：值存在vid list {0} 中，实际值：{1}'.format(TestDCSPower.vid_list, all_usb_dev_info[power_off_serial_number]['vid'].lower())):
                        assert all_usb_dev_info[power_off_serial_number]['vid'].lower() in TestDCSPower.vid_list
            with allure.step('检查redis中的模块状态判断是否下电成功'):
                module_status = get_module_status(redis_hash)
                print('module_status：', module_status)
                with check.check:
                    with allure.step('当前模块状态，期望状态：Error，实际状态：{0}'.format(module_status)):
                        assert 'Error' == module_status

    @pytest.mark.skip(reason="跳过上电测试，移远模块不支持")
    @allure.step('电源服务上电测试')
    @pytest.mark.parametrize("power_on_port", [4])
    def test_power_up(self, power_on_port):
        with allure.step('当前上电端口：{0}'.format(power_on_port)):
            # power_on_port = TestDCSPower.power_check_port
            print('power_on_port: ', power_on_port)
            redis_hash = TestDCSPower.device_id + '-DCSDeviceServer-{0}'.format(power_on_port)
            with allure.step('当前端口:{0}的redis_hash_name为：{1}'.format(power_on_port, redis_hash)):
                print('power_on_redis_hash: ', redis_hash)
        with allure.step('获取当前设备，所有usb设备的pid、vid和serial_number'):
            all_usb_dev_info = get_usb_dev_info()
            with allure.step('获取到的设备信息为：{0}'.format(all_usb_dev_info)):
                print('total_usb_dev_info: ', all_usb_dev_info)
        with allure.step('发送上电命令，并等待 80s'):
            power_on(power_on_port)
            time.sleep(80)
        with allure.step('检查设备pid、vid和serial_number，判断设备是否上电成功'):
            power_on_usb_dev_info = get_usb_dev_info()
            with allure.step('上电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_on_usb_dev_info)):
                print('power_on_usb_dev_info: ', power_on_usb_dev_info)
            two_dict_diff_key = get_two_dict_diff_key(power_on_usb_dev_info, all_usb_dev_info)
            if not two_dict_diff_key:
                with check.check:
                    with allure.step('错误，获取下电设备序列号失败，期望值：值不空，实际值：{0}'.format(two_dict_diff_key)):
                        assert two_dict_diff_key
            else:
                power_on_serial_number = two_dict_diff_key[0]
                with allure.step('上电设备的序列号为：{0}，pid、vid为：{1}'.format(
                        power_on_serial_number, power_on_usb_dev_info[power_on_serial_number])):
                    print('power_on_serial_number：{0}，pid，vid：{1}'.format(
                        power_on_serial_number, power_on_usb_dev_info[power_on_serial_number]))
                with allure.step('断言上电模块的序列号，期望值：值不为空，实际值：{0}'.format(power_on_serial_number)):
                    assert power_on_serial_number
                with allure.step('断言上电模块的pid，期望值：值存在pid list {0} 中，实际值：{1}'.format(
                        TestDCSPower.pid_list, power_on_usb_dev_info[power_on_serial_number]['pid'].lower())):
                    assert power_on_usb_dev_info[power_on_serial_number]['pid'].lower() in TestDCSPower.pid_list
                with allure.step('断言下电模块的vid，期望值：值存在vid list {0} 中，实际值：{1}'.format(
                        TestDCSPower.vid_list, power_on_usb_dev_info[power_on_serial_number]['vid'].lower())):
                    assert power_on_usb_dev_info[power_on_serial_number]['vid'].lower() in TestDCSPower.vid_list
        with allure.step('检查redis中的模块状态判断是否上电成功'):
            module_status = get_module_status(redis_hash)
            print('module_status：', module_status)
            with check.check:
                with allure.step('当前模块状态，期望状态：Servering，实际状态：{0}'.format(module_status)):
                    assert 'Servering' == module_status

    @pytest.mark.skip(reason="跳过上下电测试，移远模块不支持")
    @allure.step('电源服务上下电联合测试')
    @pytest.mark.parametrize("up_down_port", [8])
    def test_power_up_and_down(self, up_down_port):
        with allure.step('当前测试端口：{0}'.format(up_down_port)):
            print('up_down_port: ', up_down_port)
            redis_hash = TestDCSPower.device_id + '-DCSDeviceServer-{0}'.format(up_down_port)
            with allure.step('当前端口:{0}的redis_hash_name为：{1}'.format(up_down_port, redis_hash)):
                print('power_on_redis_hash: ', redis_hash)
        with allure.step('从pg数据库中获取当前支持模块的pid list和vid list'):
            pid_list, vid_list = get_pid_vid_from_pg()
            with allure.step('获取到的pid list为：{0}，获取到的vid list为：{1}'.format(pid_list, vid_list)):
                print('pid_list: ', pid_list)
                print('vid_list: ', vid_list)
        with allure.step('获取当前设备，所有usb设备的pid、vid和serial_number'):
            all_usb_dev_info = get_usb_dev_info()
            with allure.step('获取到的设备信息为：{0}'.format(all_usb_dev_info)):
                print('total_usb_dev_info: ', all_usb_dev_info)
        with allure.step('下电测试'):
            with allure.step('发送下电命令，并等待 6s'):
                power_off(up_down_port)
                print('等待 6s, 等待下电成功')
                time.sleep(6)
            with allure.step('检查设备pid、vid，判断设备是否下电成功'):
                power_off_usb_dev_info = get_usb_dev_info()
                with allure.step('下电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_off_usb_dev_info)):
                    print('power_off_usb_dev_info: ', power_off_usb_dev_info)
                two_dict_diff_key = get_two_dict_diff_key(all_usb_dev_info, power_off_usb_dev_info)
                if not two_dict_diff_key:
                    with check.check:
                        with allure.step('错误，获取下电设备序列号失败，期望值：值不空，实际值：{0}'.format(two_dict_diff_key)):
                            assert two_dict_diff_key
                else:
                    power_off_serial_number = two_dict_diff_key[0]
                    with allure.step('下电设备的序列号为：{0}，pid、vid为：{1}'.format(
                            power_off_serial_number, all_usb_dev_info[power_off_serial_number])):
                        print('serial_number：{0}，pid_and_vid：{1}'.format(
                            power_off_serial_number, all_usb_dev_info[power_off_serial_number]))
                    with allure.step('断言下电模块的pid，期望值：值存在pid list {0} 中，实际值：{1}'.format(
                            pid_list, all_usb_dev_info[power_off_serial_number]['pid'].lower())):
                        assert all_usb_dev_info[power_off_serial_number]['pid'].lower() in pid_list
                    with allure.step('断言下电模块的vid，期望值：值存在vid list {0} 中，实际值：{1}'.format(
                            vid_list, all_usb_dev_info[power_off_serial_number]['vid'].lower())):
                        assert all_usb_dev_info[power_off_serial_number]['vid'].lower() in vid_list
            with allure.step('检查redis中的模块状态判断是否下电成功'):
                module_status = get_module_status(redis_hash)
                print('module_status：', module_status)
                with check.check:
                    with allure.step('当前模块状态，期望状态：Error，实际状态：{0}'.format(module_status)):
                        assert 'Error' == module_status
        if 'Error' == module_status:
            with allure.step('上电测试'):
                with allure.step('发送上电命令，并等待 80s'):
                    power_on(up_down_port)
                    time.sleep(80)
                with allure.step('检查设备pid、vid和serial_number，判断设备是否上电成功'):
                    power_on_usb_dev_info = get_usb_dev_info()
                    with allure.step('上电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_on_usb_dev_info)):
                        print('power_on_usb_dev_info: ', power_on_usb_dev_info)
                    power_on_serial_number = get_two_dict_diff_key(power_on_usb_dev_info, power_off_usb_dev_info)[0]
                    with allure.step('上电设备的序列号为：{0}，pid、vid为：{1}'.format(
                            power_on_serial_number, all_usb_dev_info[power_on_serial_number])):
                        print('power_on_serial_number：{0}，pid，vid：{1}'.format(power_on_serial_number, all_usb_dev_info[power_on_serial_number]))
                    with allure.step('断言上电模块的序列号，期望值：{0}，实际值：{1}'.format(power_off_serial_number, power_on_serial_number)):
                        assert power_on_serial_number == power_off_serial_number
                    with allure.step('断言上电模块的pid、vid，期望值：{0}，实际值：{1}'.format(
                            all_usb_dev_info[power_off_serial_number], all_usb_dev_info[power_on_serial_number])):
                        assert all_usb_dev_info[power_on_serial_number] == all_usb_dev_info[power_off_serial_number]
                with allure.step('检查redis中的模块状态判断是否上电成功'):
                    module_status = get_module_status(redis_hash)
                    print('module_status：', module_status)
                    with check.check:
                        with allure.step('当前模块状态，期望状态：Servering，实际状态：{0}'.format(module_status)):
                            assert 'Servering' == module_status

    @allure.step('电源服务端口特殊值下电测试')
    @pytest.mark.parametrize("power_off_port", ['12g5a'])
    def test_special_value_power_down(self, power_off_port):
        with allure.step('当前下电端口：{0}'.format(power_off_port)):
            # power_off_port = '12g5a'
            print('power_off_port: ', power_off_port)
        with allure.step('获取当前设备，所有usb设备的pid、vid和serial_number'):
            all_usb_dev_info = get_usb_dev_info()
            with allure.step('获取到的设备信息为：{0}'.format(all_usb_dev_info)):
                print('total_usb_dev_info: ', all_usb_dev_info)
        with allure.step('下电测试'):
            with allure.step('发送下电命令，并等待 6s'):
                res = power_off_send_hw_port(power_off_port, power_off_port)
                with allure.step('断言命令返回值，期望值：False，实际值：{0}'.format(res['result'])):
                    assert not res['result']
                print('等待 6s, 等待下电成功')
                time.sleep(6)
            with allure.step('检查设备pid、vid，判断设备是否下电成功'):
                power_off_usb_dev_info = get_usb_dev_info()
                with allure.step('下电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_off_usb_dev_info)):
                    print('power_off_usb_dev_info: ', power_off_usb_dev_info)
                with allure.step('断言，usb设备信息，期望值：{0}，实际值：{1}'.format(all_usb_dev_info, power_off_usb_dev_info)):
                    assert power_off_usb_dev_info == all_usb_dev_info

    @allure.step('电源服务端口特殊值上电测试')
    @pytest.mark.parametrize("power_on_port", ['12g5a', '1sda2255a'])
    def test_special_value_power_up(self, power_on_port):
        with allure.step('当前上电端口：{0}'.format(power_on_port)):
            # power_on_port = '1sda2255a'
            print('power_on_port: ', power_on_port)
        with allure.step('获取当前设备，所有usb设备的pid、vid和serial_number'):
            all_usb_dev_info = get_usb_dev_info()
            with allure.step('获取到的设备信息为：{0}'.format(all_usb_dev_info)):
                print('total_usb_dev_info: ', all_usb_dev_info)
        with allure.step('上电测试'):
            with allure.step('发送下电命令，并等待 6s'):
                res = power_on_send_hw_port(power_on_port, power_on_port)
                with allure.step('断言命令返回值，期望值：False，实际值：{0}'.format(res['result'])):
                    assert not res['result']
                print('等待 6s, 等待下电成功')
                time.sleep(6)
            with allure.step('检查设备pid、vid，判断设备是否上电成功'):
                power_off_usb_dev_info = get_usb_dev_info()
                with allure.step('上电后，获取到的所有usb设备的pid、vid和serial_number信息为：{0}'.format(power_off_usb_dev_info)):
                    print('power_off_usb_dev_info: ', power_off_usb_dev_info)
                with allure.step('断言，usb设备信息，期望值：{0}，实际值：{1}'.format(all_usb_dev_info, power_off_usb_dev_info)):
                    assert power_off_usb_dev_info == all_usb_dev_info


if __name__ == "__main__":
    new_test = TestDCSPower()
    new_test.setup_class()
    power_off(4)
    # power_on(4)
