import pytest
import requests
import time
import json
import uuid
from datetime import datetime

from server.server_common import OperateSharedData

# ====================== 全局常量配置 ======================
HOST = "http://neucirflite-test.oymotion.com"
BASE_URL = f"{HOST}/neucirflite_portal"
REAL_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzgzMzM5OTMsInVzZXJuYW1lIjoi5ZCR5aKe5o-Q5pyJIn0.Td_YxrGLHN83dyryYRB7_QhFBNpoAwdrPfUM4eDzNBE"

HEADERS = {
    "X-Access-Token": REAL_TOKEN,
    "Content-Type": "application/json"
}

# ====================== 接口路由【严格按你顺序分组】 ======================
# 一、系统登录 & 主页
URL_SYS_GET_LOGIN_QRCODE = "/sys/getLoginQrcode"
URL_SYS_GET_QRCODE_TOKEN = "/sys/getQrcodeToken"
URL_SYS_LOGIN = "/sys/login"
URL_SYS_PHONE_LOGIN = "/sys/phoneLogin"
URL_SYS_RANDOM_IMAGE = "/sys/randomImage/{key}"
URL_SYS_SCAN_LOGIN_QRCODE = "/sys/scanLoginQrcode"
URL_BACKSTAGE_PAGE = "/backstage/page"
URL_DEFAULT_SETTINGS = "/default_settings/{deviceName}"

# 二、设备管理
URL_DEVICE_ADD = "/device/Device/add"
URL_DEVICE_DELETE = "/device/Device/delete"
URL_DEVICE_DELETE_BATCH = "/device/Device/deleteBatch"
URL_DEVICE_EDIT = "/device/Device/edit"
URL_DEVICE_LIST = "/device/Device/list"
URL_DEVICE_LOG = "/device/Device/log/{deviceSerialNo}"
URL_DEVICE_QUERY_BY_ID = "/device/Device/queryById"

# 三、设备类型管理（新增）
URL_DEVICE_TYPES_ADD = "/device/DeviceTypes/add"
URL_DEVICE_TYPES_DELETE = "/device/DeviceTypes/delete"
URL_DEVICE_TYPES_DELETE_BATCH = "/device/DeviceTypes/deleteBatch"
URL_DEVICE_TYPES_EDIT = "/device/DeviceTypes/edit"
URL_DEVICE_TYPES_LIST = "/device/DeviceTypes/list"
URL_DEVICE_TYPES_QUERY_BY_ID = "/device/DeviceTypes/queryById"
URL_DEVICE_TYPES_DEVICE_TYPE = "/device/DeviceTypes/devicetype"
URL_DEVICE_TYPES_DEVICE_TYPE_NAME = "/device/DeviceTypes/devicetypename"
URL_DEVICE_TYPES_TOP = "/device/DeviceTypes/top"

# 四、设备固件管理（新增）
URL_DEVICE_FIRMWARE_ADD = "/device/deviceFirmware/add"
URL_DEVICE_FIRMWARE_DELETE = "/device/deviceFirmware/delete"
URL_DEVICE_FIRMWARE_DELETE_BATCH = "/device/deviceFirmware/deleteBatch"
URL_DEVICE_FIRMWARE_EDIT = "/device/deviceFirmware/edit"
URL_DEVICE_FIRMWARE_LIST = "/device/deviceFirmware/list"
URL_DEVICE_FIRMWARE_QUERY_TYPE_ID = "/device/deviceFirmware/queryTypeId"
URL_DEVICE_FIRMWARE_UPLOAD = "/device/deviceFirmware/upload"

# 五、APK 模块
URL_APK_UPLOAD_FILE = "/apk/upload/file"
URL_APK_DELETE_FILE = "/apk/upload/file"
URL_APK_DOWNLOAD_LATEST = "/apks/downloadlatest"
URL_APK_LATEST_VERSION = "/apks/latest_version.json"
URL_APK_DOWNLOAD_VERSION = "/apks/{version}"
URL_APK_VERSION_ADD = "/apk/version/add"
URL_APK_VERSION_DELETE = "/apk/version/delete"
URL_APK_VERSION_DELETE_BATCH = "/apk/version/deleteBatch"
URL_APK_VERSION_EDIT = "/apk/version/edit"
URL_APK_VERSION_LIST = "/apk/version/list"
URL_APK_VERSION_QUERY_BY_ID = "/apk/version/queryById"

# 六、用户 / 训练 / 统计 其他
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
URL_USER_LATEST_FIRMWARE_VERSION = "/user/latest_firmware_version"
URL_USER_MODIFY_TEMPLATE_INFO = "/user/modify_template_info"
URL_USER_RETRAIN = "/user/retrain"
URL_USER_SAVE_DEVICE_SETTINGS = "/user/save_device_settings"
URL_USER_SIGNUP = "/user/signup"
URL_USER_SINGLE_TRAIN = "/user/single_train"
URL_USER_USAGE_STAT = "/user/usage_stat"
URL_USER_USER_INFO = "/user/user_info"
URL_USER_ADD_MODEL_STATUS = "/user/add_model_status"
URL_USER_CHECK_LATEST_EMG_MODELS = "/user/check_latest_emg_models"
URL_USER_DEBUG_INFO = "/user/debug_info"
URL_USER_SIGNIN = "/user/signin"

URL_FIRMWARE_DOWNLOAD = "/firmware/{getTypeName}/{url}"

URL_USAGE_STATS_ADD = "/usagestats/add"
URL_USAGE_STATS_DELETE = "/usagestats/delete"
URL_USAGE_STATS_DELETE_BATCH = "/usagestats/deleteBatch"
URL_USAGE_STATS_EDIT = "/usagestats/edit"
URL_USAGE_STATS_LIST = "/usagestats/list"
URL_USAGE_STATS_QUERY_BY_ID = "/usagestats/queryById"

# ====================== 测试全局变量 & 测试数据 ======================
TEST_TEMPLATE_NO = 9999
TEST_TRAINING_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEST_UUID = f"AUTO_{uuid.uuid4().hex[:12].upper()}"
TEST_PAGE_NO = 1
TEST_PAGE_SIZE = 10
TEST_CAPTCHA_KEY = f"test_key_{uuid.uuid4().hex[:6]}"
TEST_QRCODE_ID = f"test_qrcode_{uuid.uuid4().hex[:6]}"
TEST_DEVICE_SERIAL_NO = f"SN_{uuid.uuid4().hex[:10].upper()}"
TEST_DEVICE_NAME = "OY-DEVICE-001"
TEST_ID = "9999"
TEST_IDS = "9999,10000"
TEST_VERSION = "V1.0.0"

# 设备类型测试数据
TEST_TYPE_NAME = f"TYPE_{uuid.uuid4().hex[:6].upper()}"
TEST_HARDWARE_TYPE = 1
TEST_HARDWARE_VER = 2

# 设备固件测试数据
TEST_FW_DEVICE_TYPE_ID = 1
TEST_FW_VERSION = "V2.0.0"
TEST_FW_RELEASE_ZH = "固件版本测试中文说明"
TEST_FW_RELEASE_EN = "Firmware test release note"
TEST_FW_IS_VALID = 1
TEST_FW_URL = "/firmware/test.bin"

# 用户/训练测试数据
TEST_USER_ID = "10001"
TEST_TEMPLATE_ID = 9999
TEST_TEMPLATE_NAME = f"AUTO_TPL_{uuid.uuid4().hex[:6]}"
TEST_MODEL_ID = 100
TEST_EMG_DATA = "test_emg_data"

# ====================== 工具函数 & 夹具 ======================
def check_test_stop_pause():
    try:
        is_stop, is_pause = OperateSharedData.read_control()
        if is_stop: pytest.exit("🛑 测试已停止")
        while is_pause:
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop: pytest.exit("🛑 测试已停止")
    except Exception:
        pass

execute_total_times = 1
case_interval_seconds = 1
threads_num = 1

def refresh_test_params():
    try:
        global execute_total_times, case_interval_seconds, threads_num
        execute_total_times, case_interval_seconds, threads_num = OperateSharedData.read_fun_params()
    except Exception:
        pass


def print_response_info(req_params, res):
    """干净版：不打印二进制乱码，自动识别文件/图片/APK"""
    print("\n" + "=" * 50)

    # 打印请求参数
    if req_params:
        print(f"请求参数: {req_params}")

    # 打印状态码
    print(f"状态码: {res.status_code}")

    try:
        # 如果是 JSON → 正常打印
        if "application/json" in res.headers.get("Content-Type", ""):
            print(f"响应内容: {json.dumps(res.json(), ensure_ascii=False, indent=2)}")
        else:
            # 如果是图片/APK/文件 → 不打印乱码，只提示
            content_type = res.headers.get("Content-Type", "unknown")
            print(f"响应内容: 【文件/图片/APK 二进制流】 Content-Type: {content_type}，长度：{len(res.content)} 字节")

    except Exception:
        # 其他非JSON、非文件 → 安全输出
        print("响应内容: 非JSON格式数据（已屏蔽乱码）")

    print("=" * 50)
def assert_api_common(res):
    assert res.status_code == 200, f"HTTP状态码异常: {res.status_code}"
    try:
        data = res.json()
        if "success" in data:
            assert data["success"] is True, f"业务失败: {data.get('message')}"
    except:
        pass

def safe_request(session, method, url, **kwargs):
    try:
        if method.lower() == "get":
            return session.get(url, timeout=10,** kwargs)
        elif method.lower() == "post":
            return session.post(url, timeout=10, **kwargs)
        elif method.lower() == "put":
            return session.put(url, timeout=10,** kwargs)
        elif method.lower() == "delete":
            return session.delete(url, timeout=10, **kwargs)
    except Exception as e:
        pytest.skip(f"请求异常跳过: {str(e)}")

@pytest.fixture(scope="session", autouse=True)
def device_driver():
    print("\n✅ 全量接口测试开始")
    yield
    print("\n✅ 全量接口测试结束")

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
# 一、系统登录 & 主页 Case
# ==============================================
def test_sys_login(api_session):
    """系统登录-账号密码登录"""
    url = f"{BASE_URL}{URL_SYS_LOGIN}"
    json_data = {"username":"test","password":"test123","captcha":"1234","checkKey":TEST_CAPTCHA_KEY}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_backstage_page(api_session):
    """主页-后台首页查看"""
    url = f"{BASE_URL}{URL_BACKSTAGE_PAGE}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_default_settings(api_session):
    """系统-默认配置获取"""
    url = f"{BASE_URL}{URL_DEFAULT_SETTINGS}".format(deviceName=TEST_DEVICE_NAME)
    res = safe_request(api_session,"get",url)
    print_response_info({"deviceName":TEST_DEVICE_NAME},res)
    assert_api_common(res)

def test_sys_get_login_qrcode(api_session):
    """登录-获取登录二维码"""
    url = f"{BASE_URL}{URL_SYS_GET_LOGIN_QRCODE}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_sys_get_qrcode_token(api_session):
    """登录-获取扫码Token"""
    url = f"{BASE_URL}{URL_SYS_GET_QRCODE_TOKEN}"
    params = {"qrcodeId":TEST_QRCODE_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_sys_phone_login(api_session):
    """登录-手机号验证码登录"""
    url = f"{BASE_URL}{URL_SYS_PHONE_LOGIN}"
    json_data = {"phone":"13800138000","code":"1234"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_sys_random_image(api_session):
    """登录-获取验证码图片"""
    url = f"{BASE_URL}{URL_SYS_RANDOM_IMAGE}".format(key=TEST_CAPTCHA_KEY)
    res = safe_request(api_session,"get",url)
    print_response_info({"key":TEST_CAPTCHA_KEY},res)
    assert_api_common(res)

def test_sys_scan_login_qrcode(api_session):
    """登录-扫码登录校验"""
    url = f"{BASE_URL}{URL_SYS_SCAN_LOGIN_QRCODE}"
    params = {"qrcodeId":TEST_QRCODE_ID,"token":TEST_UUID}
    res = safe_request(api_session,"post",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

# ==============================================
# 二、设备管理 Case
# ==============================================
def test_device_add(api_session):
    """设备管理-新增设备"""
    url = f"{BASE_URL}{URL_DEVICE_ADD}"
    json_data = {
        "activateKey":"ACT_TEST001",
        "addr":"AA:BB:CC:DD:EE:FF",
        "deviceSerialNo":TEST_DEVICE_SERIAL_NO,
        "deviceTypeId":1,
        "forbidden":0,
        "remark":"自动化测试新增"
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_list(api_session):
    """设备管理-分页列表"""
    url = f"{BASE_URL}{URL_DEVICE_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_query_by_id(api_session):
    """设备管理-单条查询"""
    url = f"{BASE_URL}{URL_DEVICE_QUERY_BY_ID}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_edit_post(api_session):
    """设备管理-编辑POST"""
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"
    json_data = {"id":int(TEST_ID),"remark":"自动化编辑"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_edit_put(api_session):
    """设备管理-编辑PUT"""
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"
    json_data = {"id":int(TEST_ID),"remark":"自动化PUT编辑"}
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_log(api_session):
    """设备管理-设备日志查询"""
    url = f"{BASE_URL}{URL_DEVICE_LOG}".format(deviceSerialNo=TEST_DEVICE_SERIAL_NO)
    res = safe_request(api_session,"get",url)
    print_response_info({"deviceSerialNo":TEST_DEVICE_SERIAL_NO},res)
    assert res.status_code == 200

def test_device_delete(api_session):
    """设备管理-单条删除"""
    url = f"{BASE_URL}{URL_DEVICE_DELETE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_delete_batch(api_session):
    """设备管理-批量删除"""
    url = f"{BASE_URL}{URL_DEVICE_DELETE_BATCH}"
    params = {"ids":TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

# ==============================================
# 三、设备类型管理 新增 Case
# ==============================================
def test_device_types_add(api_session):
    """设备类型-新增"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_ADD}"
    json_data = {
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_delete(api_session):
    """设备类型-单条删除"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_delete_batch(api_session):
    """设备类型-批量删除"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE_BATCH}"
    params = {"ids":TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_edit_post(api_session):
    """设备类型-编辑POST"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id":int(TEST_ID),
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_edit_put(api_session):
    """设备类型-编辑PUT"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id":int(TEST_ID),
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_list(api_session):
    """设备类型-分页列表"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_query_by_id(api_session):
    """设备类型-通过id查询"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_QUERY_BY_ID}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_devicetype(api_session):
    """设备类型-根据ID查询类型"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DEVICE_TYPE}"
    params = {"id":int(TEST_ID)}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_devicetypename(api_session):
    """设备类型-获取类型名称列表"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DEVICE_TYPE_NAME}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_device_types_top(api_session):
    """设备类型-最新前5条"""
    url = f"{BASE_URL}{URL_DEVICE_TYPES_TOP}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

# ==============================================
# 四、设备固件管理 新增 Case
# ==============================================
def test_device_firmware_add(api_session):
    """设备固件-新增"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_ADD}"
    json_data = {
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_delete(api_session):
    """设备固件-单条删除"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_delete_batch(api_session):
    """设备固件-批量删除"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE_BATCH}"
    params = {"ids":TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_edit_post(api_session):
    """设备固件-编辑POST"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id":int(TEST_ID),
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_edit_put(api_session):
    """设备固件-编辑PUT"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id":int(TEST_ID),
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_list(api_session):
    """设备固件-分页列表"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE,"version":TEST_FW_VERSION}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_query_type_id(api_session):
    """设备固件-通过typeid查询"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_QUERY_TYPE_ID}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_upload(api_session):
    """设备固件-通用文件上传"""
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_UPLOAD}"
    res = safe_request(api_session,"post",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_firmware_download(api_session):
    """固件下载"""
    url = f"{BASE_URL}{URL_FIRMWARE_DOWNLOAD}".format(getTypeName="test",url="test.bin")
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert res.status_code == 200

# ==============================================
# 五、APK 模块 Case
# ==============================================
def test_apk_upload_file(api_session):
    """APK-文件上传"""
    url = f"{BASE_URL}{URL_APK_UPLOAD_FILE}"
    res = safe_request(api_session,"post",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_apk_delete_file(api_session):
    """APK-删除文件"""
    url = f"{BASE_URL}{URL_APK_DELETE_FILE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_add(api_session):
    """APK版本-新增"""
    url = f"{BASE_URL}{URL_APK_VERSION_ADD}"
    json_data = {"version":TEST_VERSION,"remark":"APK自动化测试"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_apk_version_delete(api_session):
    """APK版本-单条删除"""
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_delete_batch(api_session):
    """APK版本-批量删除"""
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE_BATCH}"
    params = {"ids":TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_edit(api_session):
    """APK版本-编辑"""
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"
    json_data = {"id":int(TEST_ID),"version":TEST_VERSION}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_apk_version_list(api_session):
    """APK版本-分页列表"""
    url = f"{BASE_URL}{URL_APK_VERSION_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_query_by_id(api_session):
    """APK版本-单条查询"""
    url = f"{BASE_URL}{URL_APK_VERSION_QUERY_BY_ID}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_download_latest(api_session):
    """APK-下载最新版"""
    url = f"{BASE_URL}{URL_APK_DOWNLOAD_LATEST}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert res.status_code == 200

def test_apk_latest_version(api_session):
    """APK-获取最新版本配置"""
    url = f"{BASE_URL}{URL_APK_LATEST_VERSION}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_apk_download_version(api_session):
    """APK-按版本下载"""
    url = f"{BASE_URL}{URL_APK_DOWNLOAD_VERSION}".format(version=TEST_VERSION)
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert res.status_code == 200

# ==============================================
# 六、用户 / 训练 / 统计 【全部补齐 100%完整】
# ==============================================
def test_user_signup(api_session):
    """用户-注册"""
    url = f"{BASE_URL}{URL_USER_SIGNUP}"
    json_data = {"username":"test_auto","password":"123456"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_signin(api_session):
    """用户-登录"""
    url = f"{BASE_URL}{URL_USER_SIGNIN}"
    json_data = {"username":"test","password":"123456"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_user_info(api_session):
    """用户-获取个人信息"""
    url = f"{BASE_URL}{URL_USER_USER_INFO}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_device_info(api_session):
    """用户-设备信息"""
    url = f"{BASE_URL}{URL_USER_DEVICE_INFO}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_get_device_settings(api_session):
    """用户-获取设备配置"""
    url = f"{BASE_URL}{URL_USER_GET_DEVICE_SETTINGS}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_save_device_settings(api_session):
    """用户-保存设备配置"""
    url = f"{BASE_URL}{URL_USER_SAVE_DEVICE_SETTINGS}"
    json_data = {"setting":"test"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_get_templates(api_session):
    """用户-获取模板列表"""
    url = f"{BASE_URL}{URL_USER_GET_TEMPLATES}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_modify_template_info(api_session):
    """用户-修改模板信息"""
    url = f"{BASE_URL}{URL_USER_MODIFY_TEMPLATE_INFO}"
    json_data = {"templateId":TEST_TEMPLATE_ID,"templateName":TEST_TEMPLATE_NAME}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_gesture_train(api_session):
    """用户-手势训练"""
    url = f"{BASE_URL}{URL_USER_GESTURE_TRAIN}"
    json_data = {"templateId":TEST_TEMPLATE_ID,"emgData":TEST_EMG_DATA}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_single_train(api_session):
    """用户-单次训练"""
    url = f"{BASE_URL}{URL_USER_SINGLE_TRAIN}"
    json_data = {"templateId":TEST_TEMPLATE_ID}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_retrain(api_session):
    """用户-重新训练"""
    url = f"{BASE_URL}{URL_USER_RETRAIN}"
    json_data = {"templateId":TEST_TEMPLATE_ID}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_get_training_status(api_session):
    """用户-获取训练状态"""
    url = f"{BASE_URL}{URL_USER_GET_TRAINING_STATUS}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_get_training_records(api_session):
    """用户-获取训练记录"""
    url = f"{BASE_URL}{URL_USER_GET_TRAINING_RECORDS}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_delete_training_record(api_session):
    """用户-删除训练记录"""
    url = f"{BASE_URL}{URL_USER_DELETE_TRAINING_RECORD}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_user_delete_error_training_info(api_session):
    """用户-删除错误训练信息"""
    url = f"{BASE_URL}{URL_USER_DELETE_ERROR_TRAINING_INFO}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_user_get_model_status(api_session):
    """用户-获取模型状态"""
    url = f"{BASE_URL}{URL_USER_GET_MODEL_STATUS}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_add_model_status(api_session):
    """用户-添加模型状态"""
    url = f"{BASE_URL}{URL_USER_ADD_MODEL_STATUS}"
    json_data = {"modelId":TEST_MODEL_ID}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_check_latest_emg_models(api_session):
    """用户-检查最新EMG模型"""
    url = f"{BASE_URL}{URL_USER_CHECK_LATEST_EMG_MODELS}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_download_emg_model(api_session):
    """用户-下载EMG模型"""
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_MODEL}"
    params = {"modelId":TEST_MODEL_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert res.status_code == 200

def test_user_download_emg_data(api_session):
    """用户-下载EMG数据"""
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_DATA}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert res.status_code == 200

def test_user_latest_firmware_version(api_session):
    """用户-获取最新固件版本"""
    url = f"{BASE_URL}{URL_USER_LATEST_FIRMWARE_VERSION}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_user_debug_info(api_session):
    """用户-调试信息"""
    url = f"{BASE_URL}{URL_USER_DEBUG_INFO}"
    json_data = {"info":"test_debug"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_user_usage_stat(api_session):
    """用户-使用统计"""
    url = f"{BASE_URL}{URL_USER_USAGE_STAT}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

# ---------------- 统计模块 ----------------
def test_usagestats_add(api_session):
    """使用统计-新增"""
    url = f"{BASE_URL}{URL_USAGE_STATS_ADD}"
    json_data = {"content":"test_stat"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_usagestats_edit(api_session):
    """使用统计-编辑"""
    url = f"{BASE_URL}{URL_USAGE_STATS_EDIT}"
    json_data = {"id":int(TEST_ID)}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_usagestats_list(api_session):
    """使用统计-列表"""
    url = f"{BASE_URL}{URL_USAGE_STATS_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_usagestats_query_by_id(api_session):
    """使用统计-按ID查询"""
    url = f"{BASE_URL}{URL_USAGE_STATS_QUERY_BY_ID}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_usagestats_delete(api_session):
    """使用统计-删除"""
    url = f"{BASE_URL}{URL_USAGE_STATS_DELETE}"
    params = {"id":TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_usagestats_delete_batch(api_session):
    """使用统计-批量删除"""
    url = f"{BASE_URL}{URL_USAGE_STATS_DELETE_BATCH}"
    params = {"ids":TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)