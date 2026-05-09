import pytest
import requests
import time

from server.server_common import OperateSharedData

# ====================== 【全局常量配置 - 统一提取】 ======================
# 服务配置
HOST = "http://neucirflite-test.oymotion.com"
BASE_URL = f"{HOST}/neucirflite_portal"
REAL_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzgzMzM5OTMsInVzZXJuYW1lIjoid2FuZ3J1aXdlaUBveW1vdGlvbi5jb20ifQ.Td_YxrGLHN83dyryYRB7_QhFBNpoAwdrPfUM4eDzNBE"

# 请求头
CONTENT_TYPE = "application/json"
HEADERS = {
    "X-Access-Token": REAL_TOKEN,
    "Content-Type": CONTENT_TYPE
}

# HTTP 状态码常量
HTTP_200 = 200
HTTP_400 = 400
HTTP_401 = 401
HTTP_403 = 403
HTTP_404 = 404

# ====================== 【旧接口常量】 ======================
URL_USER_DELETE_ERROR_TRAINING_INFO = "/user/delete_error_training_info"
URL_USER_DELETE_TRAINING_RECORD = "/user/delete_training_record"
URL_USER_DEVICE_INFO = "/user/device_info"
URL_USER_DOWNLOAD_EMG_DATA = "/user/download_emg_data"
URL_USER_DOWNLOAD_EMG_MODEL = "/user/download_emg_model"
URL_USER_GESTURE_TRAIN = "/user/gesture_train"
URL_USER_GET_TRAINING_STATUS = "/user/getTrainingStatus"
URL_USER_GET_DEVICE_SETTINGS = "/user/get_device_settings"
URL_USER_GET_MODEL_STATUS = "/user/get_model_status"
URL_USER_GET_TEMPLATES = "/user/get_templates"
URL_USER_GET_TRAINING_RECORDS = "/user/get_training_records"
URL_USER_LATEST_FIRMWARE_VERSION = "/user/latest_firmware_version_of_device"
URL_USER_MODIFY_TEMPLATE_INFO = "/user/modify_template_info"
URL_USER_RETRAIN = "/user/retrain"
URL_USER_SAVE_DEVICE_SETTINGS = "/user/save_device_settings"
URL_USER_SIGNUP = "/user/signup"
URL_USER_SINGLE_TRAIN = "/user/single_train"
URL_USER_USAGE_STAT = "/user/usage_stat"
URL_USER_USER_INFO = "/user/user_info"

# ====================== 【新增接口常量】 ======================
# 设备用户
URL_USER_ADD_MODEL_STATUS = "/user/add_model_status"
URL_USER_CHECK_LATEST_EMG_MODELS = "/user/check_latest_emg_models"
URL_USER_DEBUG_INFO = "/user/debug_info"
URL_USER_SIGNIN = "/user/signin"

# 用户登录
URL_SYS_GET_LOGIN_QRCODE = "/sys/getLoginQrcode"
URL_SYS_GET_QRCODE_TOKEN = "/sys/getQrcodeToken"
URL_SYS_LOGIN = "/sys/login"
URL_SYS_PHONE_LOGIN = "/sys/phoneLogin"
URL_SYS_RANDOM_IMAGE = "/sys/randomImage/{key}"
URL_SYS_SCAN_LOGIN_QRCODE = "/sys/scanLoginQrcode"

# 主页
URL_BACKSTAGE_PAGE = "/backstage/page"

# ====================== 【Swagger 新增接口】 ======================
# 默认设置
URL_DEFAULT_SETTINGS = "/default_settings/{deviceName}"
# APK 文件上传
URL_APK_UPLOAD_FILE = "/apk/upload/file"
# APK 文件删除
URL_APK_DELETE_FILE = "/apk/upload/file"
# 下载APP最新版本
URL_APK_DOWNLOAD_LATEST = "/apks/downloadlatest"
# 获取APP最新版本
URL_APK_LATEST_VERSION = "/apks/latest_version.json"
# 下载指定版本APP
URL_APK_DOWNLOAD_VERSION = "/apks/{version}"
# APK版本发布-添加
URL_APK_VERSION_ADD = "/apk_version/apkVersion/add"
# APK版本发布-删除
URL_APK_VERSION_DELETE = "/apk_version/apkVersion/delete"
# APK版本发布-批量删除
URL_APK_VERSION_DELETE_BATCH = "/apk_version/apkVersion/deleteBatch"
# APK版本发布-编辑
URL_APK_VERSION_EDIT = "/apk_version/apkVersion/edit"
# APK版本发布-分页列表
URL_APK_VERSION_LIST = "/apk_version/apkVersion/list"
# APK版本发布-根据ID查询
URL_APK_VERSION_QUERY_BY_ID = "/apk_version/apkVersion/queryById"
# 上传使用数据-添加
URL_USAGE_STATS_ADD = "/usagestats/deviceUsageStats/add"
# 上传使用数据-删除
URL_USAGE_STATS_DELETE = "/usagestats/deviceUsageStats/delete"
# 上传使用数据-批量删除
URL_USAGE_STATS_DELETE_BATCH = "/usagestats/deviceUsageStats/deleteBatch"
# 上传使用数据-编辑
URL_USAGE_STATS_EDIT = "/usagestats/deviceUsageStats/edit"
# 上传使用数据-分页列表
URL_USAGE_STATS_LIST = "/usagestats/deviceUsageStats/list"
# 上传使用数据-根据ID查询
URL_USAGE_STATS_QUERY_BY_ID = "/usagestats/deviceUsageStats/queryById"
# 下载最新固件
URL_FIRMWARE_DOWNLOAD = "/firmware/{getTypeName}/{url}"

# ====================== 测试参数常量 ======================
TEST_TEMPLATE_NO = 1
TEST_TRAINING_TIME = "2025-12-01 10:00:00"
TEST_UUID = "dev-uuid-001"
TEST_PAGE_NO = 1
TEST_CURRENT_FIRMWARE_VERSION = "V1.0.0"
TEST_TEMPLATE_ID = 1
TEST_TEMPLATE_NAME = "test_template_001"
TEST_TEMPLATE_DESCRIPTION = "模板测试描述"
TEST_ADDR = "127.0.0.1"
TEST_ACTIVATE_KEY = "activate-key-001"
TEST_EMG_MODEL_ID = 1
TEST_DEBUG_INFO = "test_debug_info_2025"
TEST_QRCODE_ID = "test_qrcode_123"
TEST_LOGIN_TOKEN = "test_token_123"
TEST_CAPTCHA_KEY = "test_key_123"

# 新增测试参数
TEST_DEVICE_NAME = "test_device"
TEST_FILE_PATH = "/test/test.apk"
TEST_VERSION = "V1.0.0"
TEST_CHANNEL = "test_channel"
TEST_ID = "1"
TEST_IDS = "1,2,3"
TEST_GET_TYPE_NAME = "test_type"
TEST_FIRMWARE_URL = "test_url"

# ====================== 全局控制函数 ======================
def check_test_stop_pause():
    try:
        is_stop, is_pause = OperateSharedData.read_control()
        if is_stop:
            pytest.exit("🛑 测试已停止")
        while is_pause:
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop:
                pytest.exit("🛑 测试已停止")
    except Exception:
        pass


# 全局动态参数
execute_total_times = 1
case_interval_seconds = 1
threads_num = 1


def refresh_test_params():
    try:
        global execute_total_times, case_interval_seconds, threads_num
        execute_total_times, case_interval_seconds, threads_num = OperateSharedData.read_fun_params()
    except Exception:
        pass


# ====================== 测试夹具 ======================
@pytest.fixture(scope="session", autouse=True)
def device_driver():
    print("\n✅ 测试会话开始 - 真实接口测试")
    yield
    print("\n✅ 测试会话结束")


@pytest.fixture(scope="function", autouse=True)
def case_control_hook():
    yield
    check_test_stop_pause()
    refresh_test_params()
    time.sleep(case_interval_seconds)


@pytest.fixture(scope="module")
def api_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    yield session
    session.close()


# ==============================================
# 【设备用户】
# ==============================================
def test_user_delete_error_training_info(api_session):
    """【设备用户】删除训练出错信息"""
    url = f"{BASE_URL}{URL_USER_DELETE_ERROR_TRAINING_INFO}"
    params = {"emg_model_id": TEST_EMG_MODEL_ID}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 删除训练出错信息成功")


def test_user_delete_training_record(api_session):
    """【设备用户】删除训练记录"""
    url = f"{BASE_URL}{URL_USER_DELETE_TRAINING_RECORD}"
    params = {"template_no": TEST_TEMPLATE_NO, "training_time": TEST_TRAINING_TIME}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 删除训练记录成功")


def test_user_device_info(api_session):
    """【设备用户】获取产品信息"""
    url = f"{BASE_URL}{URL_USER_DEVICE_INFO}"
    params = {"uuid": TEST_UUID}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取产品信息成功")


def test_user_download_emg_data(api_session):
    """【设备用户】下载训练数据"""
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_DATA}"
    params = {"template_no": TEST_TEMPLATE_NO}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 下载训练数据成功")


def test_user_download_emg_model(api_session):
    """【设备用户】应用 EMG 模型"""
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_MODEL}"
    params = {"template_no": TEST_TEMPLATE_NO, "training_time": TEST_TRAINING_TIME}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 应用 EMG 模型成功")


def test_user_gesture_train(api_session):
    """【设备用户】手势训练"""
    url = f"{BASE_URL}{URL_USER_GESTURE_TRAIN}"
    params = {
        "channel": 1, "channelNUm": 8, "gesture_count": 5, "restart": 0, "sample_rate": 1000,
        "template_description": TEST_TEMPLATE_DESCRIPTION, "template_name": TEST_TEMPLATE_NAME, "template_no": TEST_TEMPLATE_NO
    }
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 手势训练成功")


def test_user_get_training_status(api_session):
    """【设备用户】查看单机手势状态"""
    url = f"{BASE_URL}{URL_USER_GET_TRAINING_STATUS}"
    res = api_session.post(url, params={}, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 查看单机手势状态成功")


def test_user_get_device_settings(api_session):
    """【设备用户】获取设备设置记录"""
    url = f"{BASE_URL}{URL_USER_GET_DEVICE_SETTINGS}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取设备设置记录成功")


def test_user_get_model_status(api_session):
    """【设备用户】查看当前模型应用"""
    url = f"{BASE_URL}{URL_USER_GET_MODEL_STATUS}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 查看当前模型应用成功")


def test_user_get_templates(api_session):
    """【设备用户】获取所有模板信息"""
    url = f"{BASE_URL}{URL_USER_GET_TEMPLATES}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取所有模板信息成功")


def test_user_get_training_records(api_session):
    """【设备用户】获取训练记录"""
    url = f"{BASE_URL}{URL_USER_GET_TRAINING_RECORDS}"
    params = {"page_no": TEST_PAGE_NO, "template_no": TEST_TEMPLATE_NO}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取训练记录成功")


def test_user_latest_firmware_version(api_session):
    """【设备用户】获取控制板最新固件版本"""
    url = f"{BASE_URL}{URL_USER_LATEST_FIRMWARE_VERSION}"
    params = {"current_firmware_version": TEST_CURRENT_FIRMWARE_VERSION}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取控制板最新固件版本成功")


def test_user_modify_template_info(api_session):
    """【设备用户】修改模板信息"""
    url = f"{BASE_URL}{URL_USER_MODIFY_TEMPLATE_INFO}"
    params = {"template_description": TEST_TEMPLATE_DESCRIPTION, "template_id": TEST_TEMPLATE_ID, "template_name": TEST_TEMPLATE_NAME}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 修改模板信息成功")


def test_user_retrain(api_session):
    """【设备用户】重新训练"""
    url = f"{BASE_URL}{URL_USER_RETRAIN}"
    params = {"template_no": TEST_TEMPLATE_NO, "training_time": TEST_TRAINING_TIME}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 重新训练成功")


def test_user_save_device_settings(api_session):
    """【设备用户】保存设备设置记录"""
    url = f"{BASE_URL}{URL_USER_SAVE_DEVICE_SETTINGS}"
    params = {
        "cali_data": "", "ctrl_setting": "", "pid_setting": "",
        "record_id": 0, "record_name": "test_settings_001", "sensor_type": 1, "threshold_setting": ""
    }
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 保存设备设置记录成功")


def test_user_signup(api_session):
    """【设备用户】设备用户-注册"""
    url = f"{BASE_URL}{URL_USER_SIGNUP}"
    params = {
        "activate_key": TEST_ACTIVATE_KEY, "addr": TEST_ADDR, "city": "上海", "email": "test@demo.com",
        "location": "上海测试点位", "name": "测试人员", "phone_number": "13800138000", "uuid": TEST_UUID
    }
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 设备用户注册成功")


def test_user_single_train(api_session):
    """【设备用户】单机手势训练"""
    url = f"{BASE_URL}{URL_USER_SINGLE_TRAIN}"
    params = {"addr": TEST_ADDR, "channel": 1, "channelNum": 8, "gestureCount": 5, "restart": 0, "sampleRate": 1000, "templateNo": TEST_TEMPLATE_NO}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 单机手势训练成功")


def test_user_usage_stat(api_session):
    """【设备用户】上传使用数据"""
    url = f"{BASE_URL}{URL_USER_USAGE_STAT}"
    params = {
        "latitude": 31.230416, "longitude": 121.473701,
        "total_open_times_1": 10, "total_open_times_2": 20, "total_open_times_3": 30,
        "total_open_times_4": 40, "total_open_times_5": 50, "total_use_time": 1200
    }
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 上传使用数据成功")


def test_user_user_info(api_session):
    """【设备用户】设备用户-通过id查询"""
    url = f"{BASE_URL}{URL_USER_USER_INFO}"
    params = {"activate_key": TEST_ACTIVATE_KEY, "addr": TEST_ADDR}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 通过id查询用户信息成功")


# ==============================================
# 【设备用户】新增
# ==============================================
def test_user_add_model_status(api_session):
    """【设备用户】新增模型应用状态"""
    url = f"{BASE_URL}{URL_USER_ADD_MODEL_STATUS}"
    params = {"template_no": TEST_TEMPLATE_NO, "training_time": TEST_TRAINING_TIME}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 新增模型应用状态成功")


def test_user_check_latest_emg_models(api_session):
    """【设备用户】检查有无训练完成的模型"""
    url = f"{BASE_URL}{URL_USER_CHECK_LATEST_EMG_MODELS}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 检查模型完成状态成功")


def test_user_debug_info(api_session):
    """【设备用户】上传调试信息"""
    url = f"{BASE_URL}{URL_USER_DEBUG_INFO}"
    params = {"debug_info": TEST_DEBUG_INFO}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 上传调试信息成功")


def test_user_signin(api_session):
    """【设备用户】查询设备是否存在"""
    url = f"{BASE_URL}{URL_USER_SIGNIN}"
    params = {"addr": TEST_ADDR, "uuid": TEST_UUID}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 查询设备是否存在成功")


# ==============================================
# 【用户登录】
# ==============================================
@pytest.mark.skip("跳过，test_sys_get_login_qrcode")
def test_sys_get_login_qrcode(api_session):
    """【用户登录】获取登录二维码"""
    url = f"{BASE_URL}{URL_SYS_GET_LOGIN_QRCODE}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取登录二维码成功")

@pytest.mark.skip("跳过，test_sys_get_qrcode_token")
def test_sys_get_qrcode_token(api_session):
    """【用户登录】获取扫码token"""
    url = f"{BASE_URL}{URL_SYS_GET_QRCODE_TOKEN}"
    params = {"qrcodeId": TEST_QRCODE_ID}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取扫码token成功")


def test_sys_login(api_session):
    """【用户登录】账号密码登录"""
    url = f"{BASE_URL}{URL_SYS_LOGIN}"
    json_data = {"username": "test", "password": "test123", "captcha": "1234", "checkKey": TEST_CAPTCHA_KEY}
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 登录接口调用成功")

@pytest.mark.skip("跳过，test_sys_phone_login")
def test_sys_phone_login(api_session):
    """【用户登录】手机号登录"""
    url = f"{BASE_URL}{URL_SYS_PHONE_LOGIN}"
    json_data = {"phone": "13800138000", "code": "1234"}
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 手机号登录接口调用成功")

@pytest.mark.skip("跳过，test_sys_random_image")
def test_sys_random_image(api_session):
    """【用户登录】获取验证码图片"""
    url = f"{BASE_URL}{URL_SYS_RANDOM_IMAGE}".format(key=TEST_CAPTCHA_KEY)
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取验证码图片成功")

@pytest.mark.skip("跳过，test_sys_scan_login_qrcode")
def test_sys_scan_login_qrcode(api_session):
    """【用户登录】扫码登录二维码"""
    url = f"{BASE_URL}{URL_SYS_SCAN_LOGIN_QRCODE}"
    params = {"qrcodeId": TEST_QRCODE_ID, "token": TEST_LOGIN_TOKEN}
    res = api_session.post(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 扫码登录二维码成功")


# ==============================================
# 【主页】
# ==============================================
def test_backstage_page(api_session):
    """【主页】展示首页数据"""
    url = f"{BASE_URL}{URL_BACKSTAGE_PAGE}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取首页数据成功")


# ==============================================
# 【Swagger 新增接口用例】
# ==============================================
def test_default_settings(api_session):
    """【默认设置】根据设备类型获取设备默认设置"""
    url = f"{BASE_URL}{URL_DEFAULT_SETTINGS}".format(deviceName=TEST_DEVICE_NAME)
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取设备默认设置成功")


def test_apk_upload_file(api_session):
    """【APK上传】上传APK文件"""
    url = f"{BASE_URL}{URL_APK_UPLOAD_FILE}"
    files = {'file': open('test.apk', 'rb')}
    res = api_session.post(url, files=files, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 上传APK文件成功")


def test_apk_delete_file(api_session):
    """【APK上传】删除APK文件"""
    url = f"{BASE_URL}{URL_APK_DELETE_FILE}"
    params = {"filePath": TEST_FILE_PATH}
    res = api_session.delete(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 删除APK文件成功")


def test_apk_download_latest(api_session):
    """【APK下载】下载APP最新版本"""
    url = f"{BASE_URL}{URL_APK_DOWNLOAD_LATEST}"
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 下载APP最新版本成功")


def test_apk_latest_version(api_session):
    """【APK下载】获取APP最新版本"""
    url = f"{BASE_URL}{URL_APK_LATEST_VERSION}"
    params = {"channel": TEST_CHANNEL}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 获取APP最新版本成功")


def test_apk_download_version(api_session):
    """【APK下载】下载指定版本APP"""
    url = f"{BASE_URL}{URL_APK_DOWNLOAD_VERSION}".format(version=TEST_VERSION)
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 下载指定版本APP成功")


def test_apk_version_add(api_session):
    """【APK版本】添加APK版本"""
    url = f"{BASE_URL}{URL_APK_VERSION_ADD}"
    json_data = {
        "appId": "test_app_id", "channel": 1, "creator": "test", "filePath": "/test/test.apk",
        "releaseNoteEn": "test", "releaseNoteZh": "测试", "status": 1, "version": "1.0.0", "versionName": "V1.0.0"
    }
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 添加APK版本成功")


def test_apk_version_delete(api_session):
    """【APK版本】删除APK版本"""
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE}"
    params = {"id": TEST_ID}
    res = api_session.delete(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 删除APK版本成功")


def test_apk_version_delete_batch(api_session):
    """【APK版本】批量删除APK版本"""
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = api_session.delete(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 批量删除APK版本成功")


def test_apk_version_edit_post(api_session):
    """【APK版本】编辑APK版本-POST"""
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"
    json_data = {
        "id": 1, "appId": "test_app_id", "channel": 1, "creator": "test", "filePath": "/test/test.apk",
        "releaseNoteEn": "test", "releaseNoteZh": "测试", "status": 1, "version": "1.0.0", "versionName": "V1.0.0"
    }
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 编辑APK版本成功")


def test_apk_version_edit_put(api_session):
    """【APK版本】编辑APK版本-PUT"""
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"
    json_data = {
        "id": 1, "appId": "test_app_id", "channel": 1, "creator": "test", "filePath": "/test/test.apk",
        "releaseNoteEn": "test", "releaseNoteZh": "测试", "status": 1, "version": "1.0.0", "versionName": "V1.0.0"
    }
    res = api_session.put(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 编辑APK版本成功")


def test_apk_version_list(api_session):
    """【APK版本】分页查询APK版本"""
    url = f"{BASE_URL}{URL_APK_VERSION_LIST}"
    params = {"pageNo": 1, "pageSize": 10}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 分页查询APK版本成功")


def test_apk_version_query_by_id(api_session):
    """【APK版本】根据ID查询APK版本"""
    url = f"{BASE_URL}{URL_APK_VERSION_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 根据ID查询APK版本成功")


def test_usage_stats_add(api_session):
    """【使用数据】添加上传使用数据"""
    url = f"{BASE_URL}{URL_USAGE_STATS_ADD}"
    json_data = {
        "addr": TEST_ADDR, "latitude": 31.230416, "longitude": 121.473701,
        "totalOpenTimes1": 10, "totalOpenTimes2": 20, "totalUseTime": 1200
    }
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 添加上传使用数据成功")


def test_usage_stats_delete(api_session):
    """【使用数据】删除上传使用数据"""
    url = f"{BASE_URL}{URL_USAGE_STATS_DELETE}"
    params = {"id": TEST_ID}
    res = api_session.delete(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 删除上传使用数据成功")


def test_usage_stats_delete_batch(api_session):
    """【使用数据】批量删除上传使用数据"""
    url = f"{BASE_URL}{URL_USAGE_STATS_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = api_session.delete(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 批量删除上传使用数据成功")


def test_usage_stats_edit_post(api_session):
    """【使用数据】编辑上传使用数据-POST"""
    url = f"{BASE_URL}{URL_USAGE_STATS_EDIT}"
    json_data = {
        "id": 1, "addr": TEST_ADDR, "latitude": 31.230416, "longitude": 121.473701,
        "totalOpenTimes1": 10, "totalOpenTimes2": 20, "totalUseTime": 1200
    }
    res = api_session.post(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 编辑上传使用数据成功")


def test_usage_stats_edit_put(api_session):
    """【使用数据】编辑上传使用数据-PUT"""
    url = f"{BASE_URL}{URL_USAGE_STATS_EDIT}"
    json_data = {
        "id": 1, "addr": TEST_ADDR, "latitude": 31.230416, "longitude": 121.473701,
        "totalOpenTimes1": 10, "totalOpenTimes2": 20, "totalUseTime": 1200
    }
    res = api_session.put(url, json=json_data, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 编辑上传使用数据成功")


def test_usage_stats_list(api_session):
    """【使用数据】分页查询上传使用数据"""
    url = f"{BASE_URL}{URL_USAGE_STATS_LIST}"
    params = {"pageNo": 1, "pageSize": 10}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 分页查询上传使用数据成功")


def test_usage_stats_query_by_id(api_session):
    """【使用数据】根据ID查询上传使用数据"""
    url = f"{BASE_URL}{URL_USAGE_STATS_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = api_session.get(url, params=params, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 根据ID查询上传使用数据成功")


def test_firmware_download(api_session):
    """【固件下载】下载最新固件"""
    url = f"{BASE_URL}{URL_FIRMWARE_DOWNLOAD}".format(getTypeName=TEST_GET_TYPE_NAME, url=TEST_FIRMWARE_URL)
    res = api_session.get(url, timeout=10)
    print("\n======================================")
    print(f"状态码: {res.status_code}")
    print(f"返回内容: {res.text.strip()}")
    print("======================================\n")
    assert res.status_code in (HTTP_200, HTTP_401, HTTP_403, HTTP_404), f"状态码错误：{res.status_code}"
    if res.status_code == HTTP_200:
        print("✅ 下载最新固件成功")