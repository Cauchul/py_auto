import datetime
import os
import sys
import pathlib
import shutil
import pytest
import allure


class TestSimpleScenarios:

    def __init__(self):
        self.resultFile = ''
        self.new_jmx_file = ''

    def update_jmx_parameters(self, fileName, num_threads, ramp_time, duration, host='127.0.0.1') -> bool:
        '''
            :parameter fileName: jmeter JMX 文件绝对路径
            :param caseName: jmeter JMX 测试计划名字
            :param num_threads: 线程数
            :param ramp_time: 控制线程步长
            :param duration: 执行时间
            :param remark: 标志
            :param host: 负载参数
        '''
        if not os.path.exists(fileName):
            return "Jmeter 测试计划文件不存在，请检查路径: %s" % fileName

        self.new_jmx_file = '%s_%s_%s_%s_%s' % (os.path.basename(fileName).split('.')[0], num_threads, ramp_time, duration,
                                                datetime.date.today().strftime("%Y_%m_%d"))
        print("新的jmx测试计划文件名称为%s" % self.new_jmx_file)
        curdir = os.getcwd()
        self.resultFile = os.path.join(curdir, 'jmeter result', datetime.date.today().strftime("%Y%m%d"))
        if not os.path.exists(self.resultFile):
            os.makedirs(self.resultFile)

        lines = open(fileName, encoding="utf-8").readlines()
        # print("当前jmx文件的内容为: %s" % lines)
        fp = open(os.path.join(curdir, "jmeter result", self.resultFile, self.new_jmx_file) + ".jmx", "w")
        for s in lines:
            fp.write(s.replace('name="LoopController.loops">1</intProp>', 'name="LoopController.loops">-1</intProp>')
                     .replace('num_threads">1</stringProp>', 'num_threads">%s</stringProp>' % num_threads)
                     .replace('ramp_time">1</stringProp>', 'ramp_time">%s</stringProp>' % ramp_time)
                     .replace('scheduler">false</boolProp>', 'scheduler">true</boolProp>')
                     .replace('duration"></stringProp>', 'duration">%s</stringProp>' % duration))
        fp.close()
        os.chdir(self.resultFile)
        print("当前路径:%s" % os.getcwd())

    def run_jmeter_test(self) -> bool:
        cmd = 'jmeter -v'
        counter = 0
        lines = os.popen(cmd).readlines()
        for line in lines:
            if 'The Apache Software Foundation' in line:
                print("Jmeter 环境配置成功")
                break
            else:
                counter = counter + 1
        if counter > len(lines):
            print("Jmeter 环境变量配置错误")
            return False
        file_name = os.path.join(self.resultFile, self.new_jmx_file)
        for file in pathlib.Path(self.resultFile).iterdir():
            print("file exists: %s" % os.path.join(self.resultFile, file))
            if os.path.exists(os.path.join(self.resultFile, file)):
                if file.is_file():
                    if file.name.endswith(".jtl"):
                        os.remove(os.path.join(self.resultFile, file))
                    elif file.name.endswith(".log"):
                        os.remove(os.path.join(self.resultFile, file))
                else:
                    shutil.rmtree(os.path.join(self.resultFile, file), ignore_errors=True)

        cmd = "jmeter  -n -t \"%s.jmx\" -l \"%s.jtl\" -j \"%s.log\" -e -o \"%s\"" % (file_name, file_name, file_name, file_name)
        print("Jmeter 的运行参数为: %s" % cmd)
        try:
            os.system(cmd)
        except Exception as error:
            with allure.step("运行Jmeter测试异常，请检查相关测试环境和测试代码"):
                print("运行Jmeter测试异常，请检查相关测试环境和测试代码")
                return False
        return True


if __name__ == "__main__":
    host = '127.0.0.1'
    new_jmeter_parameters = TestJmeter()
    if len(sys.argv[1:]) == 4:
        print('参数个数为: %s' % len(sys.argv[1:]))
        print('可用参数列表:', str(sys.argv[1:]))
        param = sys.argv[1:]
        print("Jmeter 测试脚本名字为: %s,并发数: %s,步长: %s,执行时间: %s" % (param[0], param[1], param[2], param[3]))
        new_jmeter_parameters.update_jmx_parameters(param[0], param[1], param[2], param[3])
        new_jmeter_parameters.run_jmeter_test()
    else:
        print("参数不对")
    pass
