from Common.GobalVariabies import *

REQUIREMENT_FILE = os.path.join(PROJECT_BASE, r'TestData\requirements.txt')


def pip_install_by_requirement_file(loop=3):
    if loop < 1:
        return
    cmd = r'pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r {0}'.format(REQUIREMENT_FILE)
    res = os.system(cmd)
    print('cmd run res: ', res)
    if res:
        pip_install_by_requirement_file(loop - 1)
