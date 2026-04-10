# test_complex.py
import pytest
import time
import random
import math
import os
from datetime import datetime
from app.app_common import OperateSharedData

# 随机延时，让用例运行更慢（模拟真实接口/业务耗时）
def random_sleep():
    delay = random.uniform(0.2, 1.5)
    time.sleep(delay)

# ========================= 工具函数（模拟业务逻辑）=========================
def complex_calculate(n):
    """复杂数学计算：阶乘 + 平方和 + 对数"""
    random_sleep()
    factorial = math.factorial(n)
    square_sum = sum(i**2 for i in range(1, n+1))
    log_val = math.log(n+1) if n>0 else 0
    return factorial + square_sum + log_val

def string_process(s):
    """字符串复杂处理"""
    random_sleep()
    return s.strip().upper().replace(" ", "_")

def list_operation(lst):
    """列表复杂操作"""
    random_sleep()
    unique = sorted(list(set(lst)))
    return sum(unique) * len(unique)

def dict_validate(d):
    """字典校验"""
    random_sleep()
    return "name" in d and "age" in d and isinstance(d["age"], int)

def file_simulate_write(content):
    """模拟文件写入"""
    random_sleep()
    return len(content) > 0

# 每条用例执行前自动检查
def check_control():
    # 每次用例执行前读取全局状态
    stop_test, pause_test = OperateSharedData.read()

    # 优化点1：先检查是否要停止
    if stop_test:
        print('测试已停止')
        pytest.exit("测试进程已停止")  # pytest 必须用 exit，不能用 break

    # 优化点2：阻塞式暂停（直到恢复 或 收到停止）
    delay = 0.0
    while pause_test:
        time.sleep(0.2)
        delay += 0.2
        stop_test, pause_test = OperateSharedData.read()

        # 暂停期间也能响应停止
        if stop_test:
            print.info('测试已停止')
            pytest.exit("测试进程已停止")

    # 退出循环后再检查一次
    stop_test, _ = OperateSharedData.read()
    if stop_test:
        print.info('测试已停止')
        pytest.exit("测试进程已停止")

@pytest.fixture(autouse=True)
def auto_check():
    check_control()
    
# ========================= 25条 成功用例 =========================
def test_success_01():
    assert complex_calculate(3) == pytest.approx(6 + 14 + 1.386)

def test_success_02():
    assert complex_calculate(5) > 150

def test_success_03():
    assert string_process("  hello test  ") == "HELLO_TEST"

def test_success_04():
    assert string_process("PYTEST") == "PYTEST"

def test_success_05():
    assert list_operation([1,2,2,3,3,3]) == 18

def test_success_06():
    assert list_operation([10,20,30]) == 180

def test_success_07():
    assert dict_validate({"name":"a","age":20}) is True

def test_success_08():
    assert dict_validate({"name":"x","age":0}) is True

def test_success_09():
    assert file_simulate_write("test content") is True

def test_success_10():
    assert file_simulate_write(" ") is True

def test_success_11():
    dt = datetime.now()
    assert dt.year >= 2020

def test_success_12():
    assert abs(-123.45) == 123.45

def test_success_13():
    assert round(3.14159, 2) == 3.14

def test_success_14():
    assert max([9,5,11,2]) == 11

def test_success_15():
    assert min([9,5,11,2]) == 2

def test_success_16():
    assert "test".isalpha() is True

def test_success_17():
    assert "123".isdigit() is True

def test_success_18():
    assert [1,2,3] + [4,5] == [1,2,3,4,5]

def test_success_19():
    assert {"a":1} | {"b":2} == {"a":1,"b":2}

def test_success_20():
    assert os.path.exists(".") is True

def test_success_21():
    assert len(str(datetime.now())) > 10

def test_success_22():
    assert math.sqrt(16) == 4.0

def test_success_23():
    assert math.pow(2,10) == 1024.0

def test_success_24():
    assert isinstance([1,2,3], list) is True

def test_success_25():
    assert isinstance(123, int) is True

# ========================= 25条 失败用例 =========================
def test_fail_26():
    assert complex_calculate(3) == 9999

def test_fail_27():
    assert complex_calculate(5) < 10

def test_fail_28():
    assert string_process(" hi ") == "hi"

def test_fail_29():
    assert string_process("test") == "Test"

def test_fail_30():
    assert list_operation([1,1,1]) == 10

def test_fail_31():
    assert list_operation([2,4,6]) == 0

def test_fail_32():
    assert dict_validate({"name":"a"}) is True

def test_fail_33():
    assert dict_validate({"age":20}) is True

def test_fail_34():
    assert file_simulate_write("") is True

def test_fail_35():
    assert file_simulate_write(None) is True

def test_fail_36():
    assert datetime.now().year == 2000

def test_fail_37():
    assert abs(-123) == -123

def test_fail_38():
    assert round(2.718, 1) == 2.71

def test_fail_39():
    assert max([1,2,3]) == 2

def test_fail_40():
    assert min([1,2,3]) == 2

def test_fail_41():
    assert "test123".isalpha() is True

def test_fail_42():
    assert "123abc".isdigit() is True

def test_fail_43():
    assert [1] + [2] == [1,2,3]

def test_fail_44():
    assert {"x":1} | {"y":2} == {"x":1}

def test_fail_45():
    assert os.path.exists("not_exist.txt") is True

def test_fail_46():
    assert len(str(datetime.now())) < 5

def test_fail_47():
    assert math.sqrt(9) == 2

def test_fail_48():
    assert math.pow(3,3) == 9

def test_fail_49():
    assert isinstance(123, str) is True

def test_fail_50():
    assert isinstance("abc", int) is True