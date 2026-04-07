import datetime
import logging
import time
import pytest
from rohand.rohand_manager import RohanManager

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# # 创建一个文件处理器，用于将日志写入文件
# file_handler = logging.FileHandler('test_can_bus_protocol_log.txt')
# file_handler.setLevel(logging.DEBUG)

# # 创建一个日志格式
# log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(log_format)

# # 将文件处理器添加到日志记录器
# logger.addHandler(file_handler)
console_handler = logging.StreamHandler()

# 设置处理程序的日志级别为 INFO
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# ModBus-RTU registers for ROH
MODBUS_PROTOCOL_VERSION_MAJOR = 1

ROH_PROTOCOL_VERSION      = (1000) # R
ROH_FW_VERSION            = (1001) # R
ROH_FW_REVISION           = (1002) # R
ROH_HW_VERSION            = (1003) # R
ROH_BOOT_VERSION          = (1004) # R
ROH_NODE_ID               = (1005) # R/W
ROH_SUB_EXCEPTION         = (1006) # R
ROH_BATTERY_VOLTAGE       = (1007) # R
ROH_manager_TEST_LEVEL       = (1008) # R/W
ROH_BEEP_SWITCH           = (1009) # R/W
ROH_BEEP_PERIOD           = (1010) # W
ROH_BUTTON_PRESS_CNT      = (1011) # R/W
ROH_RECALIBRATE           = (1012) # W
ROH_START_INIT            = (1013) # W
ROH_RESET                 = (1014) # W
ROH_POWER_OFF             = (1015) # W
ROH_RESERVED0             = (1016) # R/W
ROH_RESERVED1             = (1017) # R/W
ROH_RESERVED2             = (1018) # R/W
ROH_RESERVED3             = (1019) # R/W
ROH_CALI_END0             = (1020) # R/W
ROH_CALI_END1             = (1021) # R/W
ROH_CALI_END2             = (1022) # R/W
ROH_CALI_END3             = (1023) # R/W
ROH_CALI_END4             = (1024) # R/W
ROH_CALI_END5             = (1025) # R/W
ROH_CALI_END6             = (1026) # R/W
ROH_CALI_END7             = (1027) # R/W
ROH_CALI_END8             = (1028) # R/W
ROH_CALI_END9             = (1029) # R/W
ROH_CALI_START0           = (1030) # R/W
ROH_CALI_START1           = (1031) # R/W
ROH_CALI_START2           = (1032) # R/W
ROH_CALI_START3           = (1033) # R/W
ROH_CALI_START4           = (1034) # R/W
ROH_CALI_START5           = (1035) # R/W
ROH_CALI_START6           = (1036) # R/W
ROH_CALI_START7           = (1037) # R/W
ROH_CALI_START8           = (1038) # R/W
ROH_CALI_START9           = (1039) # R/W
ROH_CALI_THUMB_POS0       = (1040) # R/W
ROH_CALI_THUMB_POS1       = (1041) # R/W
ROH_CALI_THUMB_POS2       = (1042) # R/W
ROH_CALI_THUMB_POS3       = (1043) # R/W
ROH_CALI_THUMB_POS4       = (1044) # R/W
ROH_FINGER_P0             = (1045) # R/W
ROH_FINGER_P1             = (1046) # R/W
ROH_FINGER_P2             = (1047) # R/W
ROH_FINGER_P3             = (1048) # R/W
ROH_FINGER_P4             = (1049) # R/W
ROH_FINGER_P5             = (1050) # R/W
ROH_FINGER_P6             = (1051) # R/W
ROH_FINGER_P7             = (1052) # R/W
ROH_FINGER_P8             = (1053) # R/W
ROH_FINGER_P9             = (1054) # R/W
ROH_FINGER_I0             = (1055) # R/W
ROH_FINGER_I1             = (1056) # R/W
ROH_FINGER_I2             = (1057) # R/W
ROH_FINGER_I3             = (1058) # R/W
ROH_FINGER_I4             = (1059) # R/W
ROH_FINGER_I5             = (1060) # R/W
ROH_FINGER_I6             = (1061) # R/W
ROH_FINGER_I7             = (1062) # R/W
ROH_FINGER_I8             = (1063) # R/W
ROH_FINGER_I9             = (1064) # R/W
ROH_FINGER_D0             = (1065) # R/W
ROH_FINGER_D1             = (1066) # R/W
ROH_FINGER_D2             = (1067) # R/W
ROH_FINGER_D3             = (1068) # R/W
ROH_FINGER_D4             = (1069) # R/W
ROH_FINGER_D5             = (1070) # R/W
ROH_FINGER_D6             = (1071) # R/W
ROH_FINGER_D7             = (1072) # R/W
ROH_FINGER_D8             = (1073) # R/W
ROH_FINGER_D9             = (1074) # R/W
ROH_FINGER_G0             = (1075) # R/W
ROH_FINGER_G1             = (1076) # R/W
ROH_FINGER_G2             = (1077) # R/W
ROH_FINGER_G3             = (1078) # R/W
ROH_FINGER_G4             = (1079) # R/W
ROH_FINGER_G5             = (1080) # R/W
ROH_FINGER_G6             = (1081) # R/W
ROH_FINGER_G7             = (1082) # R/W
ROH_FINGER_G8             = (1083) # R/W
ROH_FINGER_G9             = (1084) # R/W
ROH_FINGER_STATUS0        = (1085) # R
ROH_FINGER_STATUS1        = (1086) # R
ROH_FINGER_STATUS2        = (1087) # R
ROH_FINGER_STATUS3        = (1088) # R
ROH_FINGER_STATUS4        = (1089) # R
ROH_FINGER_STATUS5        = (1090) # R
ROH_FINGER_STATUS6        = (1091) # R
ROH_FINGER_STATUS7        = (1092) # R
ROH_FINGER_STATUS8        = (1093) # R
ROH_FINGER_STATUS9        = (1094) # R
ROH_FINGER_CURRENT_LIMIT0 = (1095) # R/W
ROH_FINGER_CURRENT_LIMIT1 = (1096) # R/W
ROH_FINGER_CURRENT_LIMIT2 = (1097) # R/W
ROH_FINGER_CURRENT_LIMIT3 = (1098) # R/W
ROH_FINGER_CURRENT_LIMIT4 = (1099) # R/W
ROH_FINGER_CURRENT_LIMIT5 = (1100) # R/W
ROH_FINGER_CURRENT_LIMIT6 = (1101) # R/W
ROH_FINGER_CURRENT_LIMIT7 = (1102) # R/W
ROH_FINGER_CURRENT_LIMIT8 = (1103) # R/W
ROH_FINGER_CURRENT_LIMIT9 = (1104) # R/W
ROH_FINGER_CURRENT0       = (1105) # R
ROH_FINGER_CURRENT1       = (1106) # R
ROH_FINGER_CURRENT2       = (1107) # R
ROH_FINGER_CURRENT3       = (1108) # R
ROH_FINGER_CURRENT4       = (1109) # R
ROH_FINGER_CURRENT5       = (1110) # R
ROH_FINGER_CURRENT6       = (1111) # R
ROH_FINGER_CURRENT7       = (1112) # R
ROH_FINGER_CURRENT8       = (1113) # R
ROH_FINGER_CURRENT9       = (1114) # R
ROH_FINGER_FORCE_TARGET0   = (1115) # R/W
ROH_FINGER_FORCE_TARGET1   = (1116) # R/W
ROH_FINGER_FORCE_TARGET2   = (1117) # R/W
ROH_FINGER_FORCE_TARGET3   = (1118) # R/W
ROH_FINGER_FORCE_TARGET4   = (1119) # R/W
ROH_FINGER_FORCE_TARGET5   = (1120) # R
ROH_FINGER_FORCE_TARGET6   = (1121) # R
ROH_FINGER_FORCE_TARGET7   = (1122) # R
ROH_FINGER_FORCE_TARGET8   = (1123) # R
ROH_FINGER_FORCE_TARGET9   = (1124) # R
ROH_FINGER_SPEED0         = (1125) # R/W
ROH_FINGER_SPEED1         = (1126) # R/W
ROH_FINGER_SPEED2         = (1127) # R/W
ROH_FINGER_SPEED3         = (1128) # R/W
ROH_FINGER_SPEED4         = (1129) # R/W
ROH_FINGER_SPEED5         = (1130) # R/W
ROH_FINGER_SPEED6         = (1131) # R/W
ROH_FINGER_SPEED7         = (1132) # R/W
ROH_FINGER_SPEED8         = (1133) # R/W
ROH_FINGER_SPEED9         = (1134) # R/W
ROH_FINGER_POS_TARGET0    = (1135) # R/W
ROH_FINGER_POS_TARGET1    = (1136) # R/W
ROH_FINGER_POS_TARGET2    = (1137) # R/W
ROH_FINGER_POS_TARGET3    = (1138) # R/W
ROH_FINGER_POS_TARGET4    = (1139) # R/W
ROH_FINGER_POS_TARGET5    = (1140) # R/W
ROH_FINGER_POS_TARGET6    = (1141) # R/W
ROH_FINGER_POS_TARGET7    = (1142) # R/W
ROH_FINGER_POS_TARGET8    = (1143) # R/W
ROH_FINGER_POS_TARGET9    = (1144) # R/W
ROH_FINGER_POS0           = (1145) # R
ROH_FINGER_POS1           = (1146) # R
ROH_FINGER_POS2           = (1147) # R
ROH_FINGER_POS3           = (1148) # R
ROH_FINGER_POS4           = (1149) # R
ROH_FINGER_POS5           = (1150) # R
ROH_FINGER_POS6           = (1151) # R
ROH_FINGER_POS7           = (1152) # R
ROH_FINGER_POS8           = (1153) # R
ROH_FINGER_POS9           = (1154) # R
ROH_FINGER_ANGLE_TARGET0  = (1155) # R/W
ROH_FINGER_ANGLE_TARGET1  = (1156) # R/W
ROH_FINGER_ANGLE_TARGET2  = (1157) # R/W
ROH_FINGER_ANGLE_TARGET3  = (1158) # R/W
ROH_FINGER_ANGLE_TARGET4  = (1159) # R/W
ROH_FINGER_ANGLE_TARGET5  = (1160) # R/W
ROH_FINGER_ANGLE_TARGET6  = (1161) # R/W
ROH_FINGER_ANGLE_TARGET7  = (1162) # R/W
ROH_FINGER_ANGLE_TARGET8  = (1163) # R/W
ROH_FINGER_ANGLE_TARGET9  = (1164) # R/W
ROH_FINGER_ANGLE0         = (1165) # R
ROH_FINGER_ANGLE1         = (1166) # R
ROH_FINGER_ANGLE2         = (1167) # R
ROH_FINGER_ANGLE3         = (1168) # R
ROH_FINGER_ANGLE4         = (1169) # R
ROH_FINGER_ANGLE5         = (1170) # R
ROH_FINGER_ANGLE6         = (1171) # R
ROH_FINGER_ANGLE7         = (1172) # R
ROH_FINGER_ANGLE8         = (1173) # R
ROH_FINGER_ANGLE9         = (1174) # R

ROH_FINGER_FORCE0         = (1175) # R
ROH_FINGER_FORCE1         = (1176) # R
ROH_FINGER_FORCE2         = (1177) # R
ROH_FINGER_FORCE3         = (1178) # R
ROH_FINGER_FORCE4         = (1179) # R
ROH_FINGER_FORCE5         = (1180) # R
ROH_FINGER_FORCE6         = (1181) # R
ROH_FINGER_FORCE7         = (1182) # R
ROH_FINGER_FORCE8         = (1183) # R
ROH_FINGER_FORCE9         = (1184) # R

ROH_FINGER_FORCE_P0       = (1225) # R/W
ROH_FINGER_FORCE_P1       = (1226) # R/W
ROH_FINGER_FORCE_P2       = (1227) # R/W
ROH_FINGER_FORCE_P3       = (1228) # R/W
ROH_FINGER_FORCE_P4       = (1229) # R/W

ROH_FINGER_FORCE_I0       = (1235) # R/W
ROH_FINGER_FORCE_I1       = (1236) # R/W
ROH_FINGER_FORCE_I2       = (1237) # R/W
ROH_FINGER_FORCE_I3       = (1238) # R/W
ROH_FINGER_FORCE_I4       = (1239) # R/W

ROH_FINGER_FORCE_D0       = (1245) # R/W
ROH_FINGER_FORCE_D1       = (1246) # R/W
ROH_FINGER_FORCE_D2       = (1247) # R/W
ROH_FINGER_FORCE_D3       = (1248) # R/W
ROH_FINGER_FORCE_D4       = (1249) # R/W

ROH_FINGER_FORCE_G0       = (1255) # R/W
ROH_FINGER_FORCE_G1       = (1256) # R/W
ROH_FINGER_FORCE_G2       = (1257) # R/W
ROH_FINGER_FORCE_G3       = (1258) # R/W
ROH_FINGER_FORCE_G4       = (1259) # R/W

ROH_FINGER_FORCE_EX0      = (2000) # R
ROH_FINGER_FORCE_EX0_END  = (2099) # R
ROH_FINGER_FORCE_EX1      = (2100) # R
ROH_FINGER_FORCE_EX1_END  = (2199) # R
ROH_FINGER_FORCE_EX2      = (2200) # R
ROH_FINGER_FORCE_EX2_END  = (2299) # R
ROH_FINGER_FORCE_EX3      = (2300) # R
ROH_FINGER_FORCE_EX3_END  = (2399) # R
ROH_FINGER_FORCE_EX4      = (2300) # R
ROH_FINGER_FORCE_EX4_END  = (2499) # R
ROH_FINGER_FORCE_EX5      = (2500) # R
ROH_FINGER_FORCE_EX5_END  = (2599) # R
ROH_FINGER_FORCE_EX6      = (2600) # R
ROH_FINGER_FORCE_EX6_END  = (2699) # R
ROH_FINGER_FORCE_EX7      = (2700) # R
ROH_FINGER_FORCE_EX7_END  = (2799) # R
ROH_FINGER_FORCE_EX8      = (2800) # R
ROH_FINGER_FORCE_EX8_END  = (2899) # R
ROH_FINGER_FORCE_EX9      = (2900) # R
ROH_FINGER_FORCE_EX9_END  = (2999) # R


# 当前版本号信息
PROTOCOL_VERSION = 'V1.0.0'
FW_VERSION = 'V3.0.0'
FW_REVISION = 'V0.130'
HW_VERSION = '1B01'
BOOT_VERSION = 'V1.7.0'

#设备寄存器的默认值，测试后用于恢复，否则设备可能无法使用

manager_TEST_LEVEL       = 1 # 开机自检开关， 0 时等待 ROH_START_INIT 写 1 自检，设成 1 时允许开机归零，设成 2 时允许开机完整
BEEP_SWITCH           = 1 # 蜂鸣器开关，1 时允许发声，0 时蜂鸣器静音
BEEP_PERIOD           = 500 # 蜂鸣器发声时常（单位毫)
NODE_ID               = 2 # 设备ID默认的值为2

FINGER_P0             = 25000 # 大拇指弯曲 P 值
FINGER_P1             = 25000 # 食指弯曲 P 值
FINGER_P2             = 25000 # 中指弯曲 P 值
FINGER_P3             = 25000 # 无名指弯曲 P 值
FINGER_P4             = 25000 # 小指弯曲 P 值
FINGER_P5             = 25000 # 大拇指旋转 P 值

FINGER_I0             = 200 # 大拇指弯曲 I 值
FINGER_I1             = 200 # 食指弯曲 I 值
FINGER_I2             = 200 # 中指弯曲 I 值
FINGER_I3             = 200 # 无名指弯曲 I 值
FINGER_I4             = 200 # 小指弯曲 I 值
FINGER_I5             = 200 # 大拇指旋转 I 值


FINGER_D0             = 25000 # 大拇指弯曲 D 值
FINGER_D1             = 25000 # 食指弯曲 D 值
FINGER_D2             = 25000 # 中指弯曲 D 值
FINGER_D3             = 25000 # 无名指弯曲 D 值
FINGER_D4             = 25000 # 小指弯曲 D 值
FINGER_D5             = 25000 # 大拇指旋转 D 值


FINGER_G0             = 100 # 大拇指弯曲 G 值
FINGER_G1             = 100 # 食指弯曲 G 值
FINGER_G2             = 100 # 中指弯曲 G 值
FINGER_G3             = 100 # 无名指弯曲 G 值
FINGER_G4             = 100 # 小指弯曲 G 值
FINGER_G5             = 100 # 大拇指旋转 G 值


FINGER_CURRENT_LIMIT0  = 1299 # 大拇指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT1  = 1299 # 食指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT2  = 1299 # 中指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT3  = 1299 # 无名指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT4  = 1299 # 小指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT5  = 1299 # 大拇指旋转电机电流限制值（mA）

FINGER_FORCE_TARGET0 = 0 # 大拇指力量目标值（uint16），单位 mN
FINGER_FORCE_TARGET1 = 0 # 食指力量目标值（uint16），单位 mN
FINGER_FORCE_TARGET2 = 0 # 中指力量目标值（uint16），单位 mN
FINGER_FORCE_TARGET3 = 0 # 无名指力量目标值（uint16），单位 mN
FINGER_FORCE_TARGET4 = 0 #  小指力量目标值（uint16），单位 mN


FINGER_FORCE_LIMIT0  = 15000 # 大拇指力量限制值（单位 mN）
FINGER_FORCE_LIMIT1  = 15000 # 食指指力量限制值（单位 mN）
FINGER_FORCE_LIMIT2  = 15000 # 中指力量限制值（单位 mN）
FINGER_FORCE_LIMIT3  = 15000 # 无名指力量限制值（单位 mN）
FINGER_FORCE_LIMIT4  = 15000 # 小指力量限制值（单位 mN）

FINGER_SPEED0 = 65535 # 大拇指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED1 = 65535 # 食指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED2 = 65535 # 中指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED3 = 65535 # 无名指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED4 = 65535 # 小指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED5 = 65535 # 大拇旋转逻辑速度（逻辑位置/秒）

FINGER_POS_TARGET0 = 0 #大拇指弯曲逻辑目标位置
FINGER_POS_TARGET1 = 0 #食指弯曲逻辑目标位置
FINGER_POS_TARGET2 = 0 #中指弯曲逻辑目标位置
FINGER_POS_TARGET3 = 0 #无名指弯曲逻辑目标位置
FINGER_POS_TARGET4 = 0 #小指弯曲逻辑目标位置
FINGER_POS_TARGET5 = 728 #大拇旋转指逻辑目标位置
FINGER_POS_TARGET_MAX_LOSS = 32 # 位置最大精度损失


FINGER_ANGLE_TARGET0 = 32367 # 大拇指电机轴与旋转轴夹角的目标值
FINGER_ANGLE_TARGET1 = 32367 # 食指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET2 = 32367 # 中指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET3 = 32367 # 无名指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET4 = 32367 # 小指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET5 = 0 # 大拇旋转目标角度
FINGER_ANGLE_TARGET_MAX_LOSS = 5 # 角度最大精度损失

FINGER_FORCE_P0 = 5000 #大拇指弯曲力量控制 P 值\*100（uint16），100~50000
FINGER_FORCE_P1 = 10000 #食指力量控制 P 值\*100（uint16）
FINGER_FORCE_P2 = 10000 # 中指力量控制 P 值\*100（uint16）
FINGER_FORCE_P3 = 10000 # 无名指力量控制 P 值\*100（uint16）
FINGER_FORCE_P4 = 10000 #小拇指弯曲力量控制 P 值\*100（uint16）

FINGER_FORCE_I0 = 200 #大拇指弯曲力量控制 I 值\*100（uint16），0~10000
FINGER_FORCE_I1 = 200 #食指力量控制 I 值\*100（uint16）
FINGER_FORCE_I2 = 200 # 中指力量控制 I 值\*100（uint16）
FINGER_FORCE_I3 = 200 # 无名指力量控制 I 值\*100（uint16）
FINGER_FORCE_I4 = 200 #小拇指弯曲力量控制 I 值\*100（uint16）

FINGER_FORCE_D0 = 5000 #大拇指弯曲力量控制 D 值\*100（uint16），0~50000
FINGER_FORCE_D1 = 10000 #食指力量控制 D 值\*100（uint16）
FINGER_FORCE_D2 = 10000 # 中指力量控制 D 值\*100（uint16）
FINGER_FORCE_D3 = 10000 # 无名指力量控制 D 值\*100（uint16）
FINGER_FORCE_D4 = 10000 #小拇指弯曲力量控制 D 值\*100（uint16）

FINGER_FORCE_G0 = 100 #大拇指弯曲力量控制 G 值\*100（uint16），1~100
FINGER_FORCE_G1 = 100 #食指力量控制 G 值\*100（uint16）
FINGER_FORCE_G2 = 100 # 中指力量控制 G 值\*100（uint16）
FINGER_FORCE_G3 = 100 # 无名指力量控制 G 值\*100（uint16）
FINGER_FORCE_G4 = 100 #小拇指弯曲力量控制 G 值\*100（uint16）


# WAIT_TIME = 0.1 # 延迟打印，方便查看
CLIENT_PORT = 'COM4'

TEST_START = 0X0
TEST_END = 0X3


roh_test_status_list = {
    TEST_START: '开始测试',
    TEST_END: '测试结束',
}

def print_test_info(status, info=''):
    # 检查 status 是否为合法值
    if status not in roh_test_status_list:
        raise ValueError(f"Invalid status value: {status}")

    start_message = f'###########################  {roh_test_status_list.get(status)} <{info}> ############################'
    border = '-' * len(start_message)
    logger.info(border)
    logger.info(start_message)
    logger.info(border + '\n')

def isNotNone(response):
    logger.info(f'isNotNone-->{response[0] }')
    return response is not None

@pytest.fixture(autouse=True)  # 自动运行
def manager():
    """
    pytest 夹具：初始化 modbus 连接，测试后自动关闭
    """
    manager = None
    client = None
    try:
        # 1. 创建管理器
        manager = RohanManager(RohanManager.MODBUS_PROTOCOL)
        manager.create_client(port=CLIENT_PORT)

        client = manager.client
        if client is None:
            logger.error("Modbus 客户端创建失败，跳过所有测试")
            pytest.skip("Modbus 连接失败，跳过测试")

        # 2. 把 manager 交给测试使用
        yield manager

    except Exception as e:
        logger.error(f"Modbus 初始化异常: {e}")
        pytest.skip(f"Modbus 初始化失败: {e}")

    finally:
        # 3. 无论成功失败，都保证清理（最安全）
        logger.info("开始清理 Modbus 连接")
        try:
            if manager is not None:
                manager.delete_client()
                logger.info("Modbus 连接已正常关闭")
        except Exception as close_err:
            logger.error(f"关闭连接失败: {close_err}")

def to_version(response):
    major_version = (response[0] >> 8) & 0xFF
    # 提取次版本号（低 8 位）
    minor_version = response[0] & 0xFF
    version_str = f"V{major_version}.{minor_version}"
    return version_str

def to_revision(response):
    # revision = ((response & 0xFF) << 8) | ((response >> 8) & 0xFF)
    revision = response[0]  # 高低位已经兑换过，这里不需要额外操作
    return f'V{revision}'


def test_read_protocol_version(manager):
    print_test_info(status=TEST_START, info='read protocol version')
    try:
        response = manager.read_registers(address=ROH_PROTOCOL_VERSION, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_PROTOCOL_VERSION}>失败'
        logger.info(f'读取寄存器<{ROH_PROTOCOL_VERSION}>成功,读取的值为:{to_version(response=response)}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_PROTOCOL_VERSION}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_PROTOCOL_VERSION}>失败,发生异常')

def test_read_fw_version(manager):
    print_test_info(status=TEST_START, info='read fireware version')
    try:
        response = manager.read_registers(address=ROH_FW_VERSION, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FW_VERSION}>失败'
        logger.info(f'读取寄存器<{ROH_FW_VERSION}>成功,读取的值为:{to_version(response=response)}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FW_VERSION}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FW_VERSION}>失败,发生异常')

def test_read_fw_revision(manager):
    print_test_info(status=TEST_START, info='read fireware revision')
    try:
        response = manager.read_registers(address=ROH_FW_REVISION, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FW_REVISION}>失败'
        logger.info(f'读取寄存器<{ROH_FW_REVISION}>成功,读取的值为:{to_revision(response=response)}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FW_REVISION}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FW_REVISION}>失败,发生异常')

def test_read_hw_version(manager):
    print_test_info(status=TEST_START, info='read hardware version')
    try:
        response = manager.read_registers(address=ROH_HW_VERSION, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_HW_VERSION}>失败'
        logger.info(f'读取寄存器<{ROH_HW_VERSION}>成功,读取的值为:{to_version(response=response)}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_HW_VERSION}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_HW_VERSION}>失败,发生异常')

def test_read_boot_version(manager):
    print_test_info(status=TEST_START, info='read boot loader version')
    try:
        response = manager.read_registers(address=ROH_BOOT_VERSION, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_BOOT_VERSION}>失败'
        logger.info(f'读取寄存器<{ROH_BOOT_VERSION}>成功,读取的值为:{to_version(response=response)}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_BOOT_VERSION}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_BOOT_VERSION}>失败,发生异常')

def test_read_nodeID_version(manager):
    print_test_info(status=TEST_START, info='read node id')
    try:
        response = manager.read_registers(address=ROH_NODE_ID, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_NODE_ID}>失败'
        logger.info(f'读取寄存器<{ROH_NODE_ID}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_NODE_ID}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_NODE_ID}>失败,发生异常')

# def wait_device_reboot(manager, max_attempts=180, delay_time=1, target_node_id=2):
#     """
#     优化版：先等设备重启（能连接），再等节点ID值稳定
#     """
#     attempt_count = 0
#     logger.info(f"开始等待设备重启，目标节点ID: {target_node_id}，最大等待时间: {max_attempts}秒")

#     # 第一步：等待设备重启（能创建Modbus连接+能读取寄存器）
#     while attempt_count < max_attempts:
#         logger.info(f'等待设备重启中...({attempt_count}/{max_attempts})')
#         time.sleep(delay_time)

#         bus = setup_modbus()
#         if bus is None:
#             attempt_count += 1
#             logger.warning("Modbus连接创建失败，重试...")
#             continue

#         try:
#             response = manager.read_registers(

#                address=ROH_NODE_ID,
#                 count=1,
#                 node_id=target_node_id
#             )
#             if isNotNone(response):
#                 logger.info(f"设备重启完成（能读取寄存器），开始等待值稳定...")
#                 # 第二步：等待节点ID值稳定（核心优化）
#                 wait_register_stable(
#                     target_node_id=target_node_id,
#                     target_value=target_node_id,
#                     stable_count=3,  # 连续3次读取到目标值
#                     max_attempts=30   # 额外给30秒等值稳定
#                 )
#                 return
#         except Exception as e:
#             logger.warning(f"读取节点ID失败: {e}")
#         finally:
#             attempt_count += 1

#     raise TimeoutError(f"设备重启超时（{max_attempts}秒），目标节点ID: {target_node_id}")

# @pytest.mark.skip('skip write node id, 多次写入后，等待时间过长')
# def test_write_nodeID_version(manager):
#         print_test_info(status=TEST_START, info='write node id,The normal range is [2, 247]')
#         verify_sets = [
#             3,      # 合法值
#             127,    # 合法值
#             247,    # 合法值
#             248,    # 异常值（超出上限）
#             256     # 异常值（超出上限）
#         ]
#         default_node_id = 2  # 默认设备ID
#         current_node_id = default_node_id  # 初始节点ID
#         failed_cases = []  # 记录失败用例

#         try:
#             for index, value in enumerate(verify_sets):
#                 logger.info(f"\n===== 测试用例 {index+1}: 写入节点ID = {value} =====")
#                 logger.info(f"当前通信节点ID = {current_node_id}，待写入节点ID = {value}")

#                 # 1. 写入节点ID
#                 try:
#                     write_response = manager.write_registers(
#
#                        address=ROH_NODE_ID,
#                         value=value,
#                         node_id=current_node_id
#                     )
#                     assert write_response, f"写入节点ID {value} 失败（写寄存器返回空）"
#                     logger.info(f"写入节点ID {value} 成功，等待设备重启...")
#                 except Exception as e:
#                     error_msg = f"写入节点ID {value} 失败: {e}"
#                     logger.error(error_msg)
#                     failed_cases.append(error_msg)
#                     continue

#              # 2. 等待设备重启并校验（优化后）
#                 try:
#                     # wait_device_reboot已包含值稳定校验，无需再手动读取
#                     wait_device_reboot(target_node_id=value)

#                     # 3. 区分合法/非法值的校验逻辑
#                     if 2 <= value <= 247:
#                         # 合法值：wait_device_reboot已校验值稳定，直接判定成功
#                         logger.info(f"合法值校验成功：写入{value} → 设备生效{value}")
#                         current_node_id = value
#                     else:
#                         # 非法值：重新读取一次确认（设备未写入）
#                         read_response = manager.read_registers(

#                            address=ROH_NODE_ID,
#                             count=1,
#                             node_id=default_node_id  # 非法值用默认ID读取
#                         )
#                         assert isNotNone(read_response), "重启后读取节点ID返回空"
#                         read_value = read_response[0]
#                         assert read_value != value, f"非法值校验失败（设备不应写入{value}，但读取到{read_value}）"
#                         logger.info(f"非法值校验成功：设备拒绝写入{value}，实际读取{read_value}")
#                         current_node_id = default_node_id
#                 except TimeoutError as e:
#                     error_msg = f"节点ID {value} 重启超时: {e}"
#                     logger.error(error_msg)
#                     failed_cases.append(error_msg)
#                 except AssertionError as e:
#                     error_msg = f"节点ID {value} 校验失败: {e}"
#                     logger.error(error_msg)
#                     failed_cases.append(error_msg)
#                 except Exception as e:
#                     error_msg = f"节点ID {value} 测试异常: {e}"
#                     logger.error(error_msg)
#                     failed_cases.append(error_msg)
#         finally:
#             # 无论测试成功/失败，强制恢复默认节点ID
#             logger.info("\n===== 恢复默认节点ID =====")
#             recover_success = False
#             recover_attempts = 3  # 恢复失败时重试3次
#             recover_delay = 5     # 重试间隔5秒
#             target_recover_id = NODE_ID  # 默认节点ID

#             for recover_attempt in range(recover_attempts):
#                 try:
#                     # 关闭旧连接，重新创建（避免缓存）
#                     if bus:
#                         bus.close()
#                     bus = setup_modbus()
#                     if bus is None:
#                         logger.warning(f"恢复默认值第{recover_attempt+1}次：Modbus连接失败，重试...")
#                         time.sleep(recover_delay)
#                         continue

#                     # 写入默认节点ID
#                     write_response2 = manager.write_registers(
#
#                        address=ROH_NODE_ID,
#                         value=target_recover_id,
#                         node_id=current_node_id  # 用当前通信ID写入
#                     )
#                     assert write_response2, "写入默认值失败"

#                     # 等待重启+值稳定
#                     wait_device_reboot(
#                         max_attempts=180,
#                         delay_time=1,
#                         target_node_id=target_recover_id
#                     )

#                     # 校验恢复结果（修复data变量错误）
#                     read_response2 = manager.read_registers(

#                        address=ROH_NODE_ID,
#                         count=1,
#                         node_id=target_recover_id
#                     )
#                     assert isNotNone(read_response2), "读取恢复后的节点ID返回空"
#                     read_recover_value = read_response2.registers[0]
#                     assert read_recover_value == target_recover_id, \
#                         f"恢复默认值失败（预期: {target_recover_id}, 实际: {read_recover_value}）"

#                     logger.info(f"恢复默认值成功（第{recover_attempt+1}次尝试）")
#                     recover_success = True
#                     break
#                 except Exception as e:
#                     logger.error(f"恢复默认值第{recover_attempt+1}次失败: {e}")
#                     time.sleep(recover_delay)

#             if not recover_success:
#                 pytest.fail(f"恢复默认值失败（重试{recover_attempts}次均失败）")
#             # 最终关闭连接
#             if bus:
#                 bus.close()


def test_read_battery_voltage(manager):
    print_test_info(status=TEST_START, info='read battery_voltage')
    try:
        response = manager.read_registers(address=ROH_BATTERY_VOLTAGE, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_BATTERY_VOLTAGE}>失败'
        logger.info(f'读取寄存器<{ROH_BATTERY_VOLTAGE}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_BATTERY_VOLTAGE}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_BATTERY_VOLTAGE}>失败,发生异常')

def test_read_manager_test_level(manager):
    print_test_info(status=TEST_START, info='read manager test level')
    try:
        response = manager.read_registers(address=ROH_manager_TEST_LEVEL, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_manager_TEST_LEVEL}>失败'
        logger.info(f'读取寄存器<{ROH_manager_TEST_LEVEL}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_manager_TEST_LEVEL}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_manager_TEST_LEVEL}>失败,发生异常')

def test_write_manager_test_level(manager):
    print_test_info(status=TEST_START, info='write manager test level,The normal range is {0, 1, 2}, and the out-of-range values fall within {3, 65535}')
    verify_sets = [
        0,
        1,
        2,
        3,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_manager_TEST_LEVEL, value=[value],device_id = NODE_ID)
            data = value #将值转换成十进制
            if index > 2:
                assert not response, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_manager_TEST_LEVEL, count=1)
                assert read_response[0] == data, f"从寄存器{ROH_manager_TEST_LEVEL}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_manager_TEST_LEVEL}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_manager_TEST_LEVEL}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_manager_TEST_LEVEL}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_manager_TEST_LEVEL, value=manager_TEST_LEVEL,device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_beep_switch(manager):
    print_test_info(status=TEST_START, info='read beep switch')
    try:
        response = manager.read_registers(address=ROH_BEEP_SWITCH, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_BEEP_SWITCH}>失败'
        logger.info(f'读取寄存器<{ROH_BEEP_SWITCH}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_BEEP_SWITCH}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_BEEP_SWITCH}>失败,发生异常')

def test_write_beep_switch(manager):
    print_test_info(status=TEST_START, info='write beep switch,The normal range is 0 or not 0')
    verify_sets = [
        0,
        1,
        255
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_BEEP_SWITCH, value=[value],device_id = NODE_ID)
            data = value
            if index > 0:
                expected_data = 1
            else :
                expected_data = 0
            read_response = manager.read_registers(address=ROH_BEEP_SWITCH, count=1,device_id = NODE_ID)
            assert read_response[0] == expected_data, f"从寄存器{ROH_BEEP_SWITCH}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_BEEP_SWITCH}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_BEEP_SWITCH}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_BEEP_SWITCH}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_BEEP_SWITCH, value=[BEEP_SWITCH],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_write_beep_period(manager):
    print_test_info(status=TEST_START, info='write beep period,The normal range is [1,65535], and the out-of-range values fall within [0]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_BEEP_PERIOD, value=[value],device_id = NODE_ID)
            data = value
            if index ==0:
                assert not response, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                # read_response = manager.read_registers(address=ROH_BEEP_PERIOD, count=1)
                assert response, f"写寄存器{ROH_BEEP_PERIOD}失败，写入值为{data}"
                logger.info(f"写寄存器{ROH_BEEP_PERIOD}成功,写入值为{data}\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_BEEP_PERIOD}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_BEEP_PERIOD}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_BEEP_PERIOD, value=[BEEP_PERIOD],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_P0(manager):
    print_test_info(status=TEST_START,info='read finger P0')
    try:
        response = manager.read_registers(address=ROH_FINGER_P0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P0}>失败,发生异常')

def test_write_finger_P0(manager):
    print_test_info(status=TEST_START, info='write finger P0,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P0, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P0, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P0, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P0, value=[FINGER_P0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_P1(manager):
    print_test_info(status=TEST_START,info='read finger P1')
    try:
        response = manager.read_registers(address=ROH_FINGER_P1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P1}>失败,发生异常')

def test_write_finger_P1(manager):
    print_test_info(status=TEST_START, info='write finger P1,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P1, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P1, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P1, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P1, value=[FINGER_P1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_P2(manager):
    print_test_info(status=TEST_START,info='read finger P2')
    try:
        response = manager.read_registers(address=ROH_FINGER_P2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P2}>失败,发生异常')

def test_write_finger_P2(manager):
    print_test_info(status=TEST_START, info='write finger P2,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P2, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P2, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P2, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P2, value=[FINGER_P2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_P3(manager):
    print_test_info(status=TEST_START,info='read finger P3')
    try:
        response = manager.read_registers(address=ROH_FINGER_P3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P3}>失败,发生异常')

def test_write_finger_P3(manager):
    print_test_info(status=TEST_START, info='write finger P3,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P3, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P3, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P3, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P3, value=[FINGER_P3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_P4(manager):
    print_test_info(status=TEST_START,info='read finger P4')
    try:
        response = manager.read_registers(address=ROH_FINGER_P4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P4}>失败,发生异常')

def test_write_finger_P4(manager):
    print_test_info(status=TEST_START, info='write finger P4,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P4, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P4, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P4, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P4, value=[FINGER_P4],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_P5(manager):
    print_test_info(status=TEST_START,info='read finger P5')
    try:
        response = manager.read_registers(address=ROH_FINGER_P5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_P5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_P5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_P5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_P5}>失败,发生异常')

def test_write_finger_P5(manager):
    print_test_info(status=TEST_START, info='write finger P5,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_P5, value=[value],device_id = NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_P5, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_P5, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_P5}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_P5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_P5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_P5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_P5, value=[FINGER_P5],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_I0(manager):
    print_test_info(status=TEST_START,info='read finger I0')
    try:
        response = manager.read_registers(address=ROH_FINGER_I0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I0}>失败,发生异常')

def test_write_finger_I0(manager):
    print_test_info(status=TEST_START, info='write finger I0,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I0, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I0, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I0, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I0, value=[FINGER_I0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_I1(manager):
    print_test_info(status=TEST_START,info='read finger I1')
    try:
        response = manager.read_registers(address=ROH_FINGER_I1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I1}>失败,发生异常')

def test_write_finger_I1(manager):
    print_test_info(status=TEST_START, info='write finger I1,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I1, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I1, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I1, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I1, value=[FINGER_I1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_I2(manager):
    print_test_info(status=TEST_START,info='read finger I2')
    try:
        response = manager.read_registers(address=ROH_FINGER_I2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I2}>失败,发生异常')

def test_write_finger_I2(manager):
    print_test_info(status=TEST_START, info='write finger I2,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I2, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I2, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I2, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I2, value=[FINGER_I2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_I3(manager):
    print_test_info(status=TEST_START,info='read finger I3')
    try:
        response = manager.read_registers(address=ROH_FINGER_I3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I3}>失败,发生异常')

def test_write_finger_I3(manager):
    print_test_info(status=TEST_START, info='write finger I3,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I3, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I3, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I3, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I3, value=[FINGER_I3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_I4(manager):
    print_test_info(status=TEST_START,info='read finger I4')
    try:
        response = manager.read_registers(address=ROH_FINGER_I4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I4}>失败,发生异常')

def test_write_finger_I4(manager):
    print_test_info(status=TEST_START, info='write finger I4,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I4, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I4, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I4, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I4, value=[FINGER_I4],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_I5(manager):
    print_test_info(status=TEST_START,info='read finger I5')
    try:
        response = manager.read_registers(address=ROH_FINGER_I5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_I5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_I5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_I5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_I5}>失败,发生异常')

def test_write_finger_I5(manager):
    print_test_info(status=TEST_START, info='write finger I5,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_I5, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_I5, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_I5, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_I5}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_I5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_I5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_I5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_I5, value=[FINGER_I5],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_D0(manager):
    print_test_info(status=TEST_START,info='read finger D0')
    try:
        response = manager.read_registers(address=ROH_FINGER_D0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D0}>失败,发生异常')

def test_write_finger_D0(manager):
    print_test_info(status=TEST_START, info='write finger D0,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D0, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D0, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D0, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D0, value=[FINGER_D0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_D1(manager):
    print_test_info(status=TEST_START,info='read finger D1')
    try:
        response = manager.read_registers(address=ROH_FINGER_D1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D1}>失败,发生异常')

def test_write_finger_D1(manager):
    print_test_info(status=TEST_START, info='write finger D1,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D1, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D1, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D1, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D1, value=[FINGER_D1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_D2(manager):
    print_test_info(status=TEST_START,info='read finger D2')
    try:
        response = manager.read_registers(address=ROH_FINGER_D2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D2}>失败,发生异常')

def test_write_finger_D2(manager):
    print_test_info(status=TEST_START, info='write finger D2,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D2, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D2, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D2, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D2, value=[FINGER_D2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_D3(manager):
    print_test_info(status=TEST_START,info='read finger D3')
    try:
        response = manager.read_registers(address=ROH_FINGER_D3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D3}>失败,发生异常')

def test_write_finger_D3(manager):
    print_test_info(status=TEST_START, info='write finger D3,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D3, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D3, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D3, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D3, value=[FINGER_D3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_D4(manager):
    print_test_info(status=TEST_START,info='read finger D4')
    try:
        response = manager.read_registers(address=ROH_FINGER_D4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D4}>失败,发生异常')

def test_write_finger_D4(manager):
    print_test_info(status=TEST_START, info='write finger D4,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D4, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D4, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D4, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D4, value=[FINGER_D4],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_D5(manager):
    print_test_info(status=TEST_START,info='read finger D5')
    try:
        response = manager.read_registers(address=ROH_FINGER_D5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_D5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_D5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_D5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_D5}>失败,发生异常')

def test_write_finger_D5(manager):
    print_test_info(status=TEST_START, info='write finger D5,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_D5, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_D5, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_D5, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_D5}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_D5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_D5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_D5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_D5, value=[FINGER_D5],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_G0(manager):
    print_test_info(status=TEST_START,info='read finger G0')
    try:
        response = manager.read_registers(address=ROH_FINGER_G0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G0}>成功,读取的值为:{response}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G0}>失败,发生异常')

def test_write_finger_G0(manager):
    print_test_info(status=TEST_START, info='write finger G0,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G0, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G0, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G0, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G0, value=[FINGER_G0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_G1(manager):
    print_test_info(status=TEST_START,info='read finger G1')
    try:
        response = manager.read_registers(address=ROH_FINGER_G1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G1}>失败,发生异常')

def test_write_finger_G1(manager):
    print_test_info(status=TEST_START, info='write finger G1,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G1, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G1, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G1, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G1, value=[FINGER_G1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_G2(manager):
    print_test_info(status=TEST_START,info='read finger G2')
    try:
        response = manager.read_registers(address=ROH_FINGER_G2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G2}>失败,发生异常')

def test_write_finger_G2(manager):
    print_test_info(status=TEST_START, info='write finger G2,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G2, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G2, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G2, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G2, value=[FINGER_G2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_G3(manager):
    print_test_info(status=TEST_START,info='read finger G3')
    try:
        response = manager.read_registers(address=ROH_FINGER_G3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G3}>失败,发生异常')

def test_write_finger_G3(manager):
    print_test_info(status=TEST_START, info='write finger G3,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G3, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G3, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G3, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G3, value=[FINGER_G3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_G4(manager):
    print_test_info(status=TEST_START,info='read finger G4')
    try:
        response = manager.read_registers(address=ROH_FINGER_G4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G4}>失败,发生异常')

def test_write_finger_G4(manager):
    print_test_info(status=TEST_START, info='write finger G4,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G4, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G4, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G4, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G4, value=[FINGER_G4],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_G5(manager):
    print_test_info(status=TEST_START,info='read finger G5')
    try:
        response = manager.read_registers(address=ROH_FINGER_G5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_G5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_G5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_G5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_G5}>失败,发生异常')

def test_write_finger_G5(manager):
    print_test_info(status=TEST_START, info='write finger G5,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_G5, value=[value],device_id = NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_G5, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_G5, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_G5}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_G5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_G5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_G5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_G5, value=FINGER_G5)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_status0(manager):
    print_test_info(status=TEST_START,info='read finger status0')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS0}>失败,发生异常')

def test_read_finger_status1(manager):
    print_test_info(status=TEST_START,info='read finger status1')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS1}>失败,发生异常')

def test_read_finger_status2(manager):
    print_test_info(status=TEST_START,info='read finger status2')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS2}>失败,发生异常')

def test_read_finger_status3(manager):
    print_test_info(status=TEST_START,info='read finger status3')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS3}>失败,发生异常')

def test_read_finger_status4(manager):
    print_test_info(status=TEST_START,info='read finger status4')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS4}>失败,发生异常')

def test_read_finger_status5(manager):
    print_test_info(status=TEST_START,info='read finger status5')
    try:
        response = manager.read_registers(address=ROH_FINGER_STATUS5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_STATUS5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_STATUS5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_STATUS5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_STATUS5}>失败,发生异常')

def test_read_finger_current_limit0(manager):
    print_test_info(status=TEST_START,info='read finger current limit0')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT0}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit0(manager):
    print_test_info(status=TEST_START, info='write finger current limit0,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT0, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT0, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT0, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT0, value=[FINGER_CURRENT_LIMIT0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current_limit1(manager):
    print_test_info(status=TEST_START,info='read finger current limit1')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT1}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit1(manager):
    print_test_info(status=TEST_START, info='write finger current limit1,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT1, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT1, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT1, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT1, value=[FINGER_CURRENT_LIMIT1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current_limit2(manager):
    print_test_info(status=TEST_START,info='read finger current limit2')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT2}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit2(manager):
    print_test_info(status=TEST_START, info='write finger current limit2,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT2, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT2, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT2, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT2, value=[FINGER_CURRENT_LIMIT2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current_limit3(manager):
    print_test_info(status=TEST_START,info='read finger current limit3')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT3}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit3(manager):
    print_test_info(status=TEST_START, info='write finger current limit3,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT3, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT3, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT3, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT3, value=[FINGER_CURRENT_LIMIT3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current_limit4(manager):
    print_test_info(status=TEST_START,info='read finger current limit4')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT4}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit4(manager):
    print_test_info(status=TEST_START, info='write finger current limit4,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT4, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT4, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT4, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT4, value=[FINGER_CURRENT_LIMIT4],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current_limit5(manager):
    print_test_info(status=TEST_START,info='read finger current limit5')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT_LIMIT5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT_LIMIT5}>失败,发生异常')

# @pytest.mark.skip('1200边界值写入后,读出来是1178,需要研发修改')
def test_write_current_limit5(manager):
    print_test_info(status=TEST_START, info='write finger current limit5,The normal range is [0,1299], and the out-of-range values fall within {1300,65535}')
    verify_sets = [
        0,# 0
        600,# 600
        1299,# 1299
        1300,# 1300
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT5, value=[value],device_id = NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT5, count=1,device_id = NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT5, count=1,device_id = NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_CURRENT_LIMIT5}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_CURRENT_LIMIT5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_CURRENT_LIMIT5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_CURRENT_LIMIT5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT5, value=[FINGER_CURRENT_LIMIT5],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_current0(manager):
    print_test_info(status=TEST_START,info='read finger current0')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT0}>失败,发生异常')

def test_read_finger_current1(manager):
    print_test_info(status=TEST_START,info='read finger current1')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT1}>失败,发生异常')

def test_read_finger_current2(manager):
    print_test_info(status=TEST_START,info='read finger current2')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT2}>失败,发生异常')

def test_read_finger_current3(manager):
    print_test_info(status=TEST_START,info='read finger current3')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT3}>失败,发生异常')

def test_read_finger_current4(manager):
    print_test_info(status=TEST_START,info='read finger current4')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT4}>失败,发生异常')

def test_read_finger_current5(manager):
    print_test_info(status=TEST_START,info='read finger current5')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_CURRENT5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_CURRENT5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_CURRENT5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_CURRENT5}>失败,发生异常')

def test_read_finger_force0(manager):
    print_test_info(status=TEST_START,info='read finger force0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE0}>失败,发生异常')

def test_read_finger_force1(manager):
    print_test_info(status=TEST_START,info='read finger force1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE1}>失败,发生异常')

def test_read_finger_force2(manager):
    print_test_info(status=TEST_START,info='read finger force2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE2}>失败,发生异常')

def test_read_finger_force3(manager):
    print_test_info(status=TEST_START,info='read finger force3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE3}>失败,发生异常')

def test_read_finger_force4(manager):
    print_test_info(status=TEST_START,info='read finger force4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE4}>失败,发生异常')

def test_read_finger_force_target0(manager):
    print_test_info(status=TEST_START,info='read finger force target0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_TARGET0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_TARGET0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_TARGET0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_TARGET0}>失败,发生异常')

def test_write_finger_force_target0(manager):
    print_test_info(status=TEST_START, info='write finger force target0,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET0, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET0, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_TARGET0}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_FORCE_TARGET0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_TARGET0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_TARGET0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET0, value=[FINGER_FORCE_TARGET0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_target1(manager):
    print_test_info(status=TEST_START,info='read finger force target1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_TARGET1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_TARGET1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_TARGET1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_TARGET1}>失败,发生异常')

def test_write_finger_force_target1(manager):
    print_test_info(status=TEST_START, info='write finger force target1,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET1, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET1, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_TARGET1}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_FORCE_TARGET1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_TARGET1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_TARGET1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET1, value=[FINGER_FORCE_TARGET1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_target2(manager):
    print_test_info(status=TEST_START,info='read finger force target2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_TARGET2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_TARGET2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_TARGET2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_TARGET2}>失败,发生异常')

def test_write_finger_force_target2(manager):
    print_test_info(status=TEST_START, info='write finger force target2,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET2, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET2, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_TARGET2}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_FORCE_TARGET2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_TARGET2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_TARGET2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET2, value=[FINGER_FORCE_TARGET2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_target3(manager):
    print_test_info(status=TEST_START,info='read finger force target3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_TARGET3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_TARGET3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_TARGET3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_TARGET3}>失败,发生异常')

def test_write_finger_force_target3(manager):
    print_test_info(status=TEST_START, info='write finger force target3,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET3, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET3, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_TARGET3}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_FORCE_TARGET3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_TARGET3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_TARGET3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET3, value=[FINGER_FORCE_TARGET3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_target4(manager):
    print_test_info(status=TEST_START,info='read finger force target4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_TARGET4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_TARGET4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_TARGET4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_TARGET4}>失败,发生异常')

def test_write_finger_force_target4(manager):
    print_test_info(status=TEST_START, info='write finger force target4,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET4, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_FORCE_TARGET4, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_TARGET4}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_FORCE_TARGET4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_TARGET4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_TARGET4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_TARGET4, value=[FINGER_FORCE_TARGET4])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed0(manager):
    print_test_info(status=TEST_START,info='read finger speed0')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED0}>失败,发生异常')

def test_write_finger_speed0(manager):
    print_test_info(status=TEST_START, info='write finger speed0,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED0, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED0, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED0}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED0, value=[FINGER_SPEED0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed1(manager):
    print_test_info(status=TEST_START,info='read finger speed1')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED1}>失败,发生异常')

def test_write_finger_speed1(manager):
    print_test_info(status=TEST_START, info='write finger speed1,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED1, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED1, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED1}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED1, value=[FINGER_SPEED1],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed2(manager):
    print_test_info(status=TEST_START,info='read finger speed2')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED2}>失败,发生异常')

def test_write_finger_speed2(manager):
    print_test_info(status=TEST_START, info='write finger speed2,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED2, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED2, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED2}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED2, value=[FINGER_SPEED2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed3(manager):
    print_test_info(status=TEST_START,info='read finger speed3')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED3}>失败,发生异常')

def test_write_finger_speed3(manager):
    print_test_info(status=TEST_START, info='write finger speed3,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED3, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED3, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED3}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED3, value=[FINGER_SPEED3],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed4(manager):
    print_test_info(status=TEST_START,info='read finger speed4')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED4}>失败,发生异常')

def test_write_finger_speed4(manager):
    print_test_info(status=TEST_START, info='write finger speed4,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED4, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED4, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED4}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED4, value=[FINGER_SPEED4])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_speed5(manager):
    print_test_info(status=TEST_START,info='read finger speed5')
    try:
        response = manager.read_registers(address=ROH_FINGER_SPEED5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_SPEED5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_SPEED5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_SPEED5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_SPEED5}>失败,发生异常')

def test_write_finger_speed5(manager):
    print_test_info(status=TEST_START, info='write finger speed5,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_SPEED5, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_SPEED5, count=1,device_id = NODE_ID)
            assert read_response[0] == data, f"从寄存器{ROH_FINGER_SPEED5}读出的值{read_response[0]}与写入的值{data}不匹配"
            logger.info(f"从寄存器{ROH_FINGER_SPEED5}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_SPEED5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_SPEED5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_SPEED5, value=[FINGER_SPEED5])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target0(manager):
    print_test_info(status=TEST_START,info='read finger pos target0')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET0}>失败,发生异常')

def test_write_finger_pos_target0(manager):
    print_test_info(status=TEST_START, info='write finger pos target0,The normal range is [0,65535]')
    verify_sets = [
        # 0,
        # 1,
        728,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET0, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET0, count=1,device_id = NODE_ID)
            assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET0, value=[FINGER_POS_TARGET0],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target1(manager):
    print_test_info(status=TEST_START,info='read finger pos target1')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET1}>失败,发生异常')

def test_write_finger_pos_target1(manager):
    print_test_info(status=TEST_START, info='write finger pos target1,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET1, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET1, count=1,device_id = NODE_ID)
            assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET1, value=[FINGER_POS_TARGET1])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target2(manager):
    print_test_info(status=TEST_START,info='read finger pos target2')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET2}>失败,发生异常')

def test_write_finger_pos_target2(manager):
    print_test_info(status=TEST_START, info='write finger pos target2,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET2, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET2, count=1,device_id = NODE_ID)
            assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET2, value=[FINGER_POS_TARGET2],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target3(manager):
    print_test_info(status=TEST_START,info='read finger pos target3')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET3}>失败,发生异常')

def test_write_finger_pos_target3(manager):
    print_test_info(status=TEST_START, info='write finger pos target3,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET3, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET3, count=1,device_id = NODE_ID)
            assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET3, value=[FINGER_POS_TARGET3])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target4(manager):
    print_test_info(status=TEST_START,info='read finger pos target4')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET4}>失败,发生异常')

def test_write_finger_pos_target4(manager):
    print_test_info(status=TEST_START, info='write finger pos target4,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET4, value=[value],device_id = NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET4, count=1,device_id = NODE_ID)
            assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET4, value=[FINGER_POS_TARGET4])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos_target5(manager):
    print_test_info(status=TEST_START,info='read finger pos target5')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS_TARGET5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS_TARGET5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS_TARGET5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS_TARGET5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS_TARGET5}>失败,发生异常')

def test_write_finger_pos_target5(manager): #从寄存器1140读出的值728与写入的值0比较
    print_test_info(status=TEST_START, info='write finger pos target5,The normal range is [0,65535]')
    verify_sets = [
        0,
        1,
        728,
        32767,
        32768,
        65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_POS_TARGET5, value=[value])
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_POS_TARGET5, count=1,device_id = NODE_ID)
            if index in(0,1,2):
                assert read_response[0] == FINGER_POS_TARGET5, f"从寄存器{ROH_FINGER_POS_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            else:
                assert abs(read_response[0] - data) <= FINGER_POS_TARGET_MAX_LOSS, f"从寄存器{ROH_FINGER_POS_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n"
            logger.info(f"从寄存器{ROH_FINGER_POS_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_POS_TARGET5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_POS_TARGET5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_POS_TARGET5, value=[FINGER_POS_TARGET5],device_id = NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_pos0(manager):
    print_test_info(status=TEST_START,info='read finger pos0')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS0}>失败,发生异常')

def test_read_finger_pos1(manager):
    print_test_info(status=TEST_START,info='read finger pos1')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS1, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS1}>失败,发生异常')

def test_read_finger_pos2(manager):
    print_test_info(status=TEST_START,info='read finger pos2')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS2, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS2}>失败,发生异常')

def test_read_finger_pos3(manager):
    print_test_info(status=TEST_START,info='read finger pos3')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS3, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS3}>失败,发生异常')

def test_read_finger_pos4(manager):
    print_test_info(status=TEST_START,info='read finger pos4')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS4, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS4}>失败,发生异常')

def test_read_finger_pos5(manager):
    print_test_info(status=TEST_START,info='read finger pos5')
    try:
        response = manager.read_registers(address=ROH_FINGER_POS5, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_POS5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_POS5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_POS5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_POS5}>失败,发生异常')

def get_min_angle(manager,addr):
    values = 0
    if manager.write_registers(address=addr,value=[values],device_id = NODE_ID):
       response = manager.read_registers(address=addr,count=1,device_id = NODE_ID)
       logger.info(f'get min angle : {addr} ->{response[0]}')
       return response[0]
    else:
        logger.info(f'get min angle : {addr} 尝试获取最小值失败')
        return 0

def get_max_angle(manager,addr):
    values = 32767
    if manager.write_registers(address=addr,value=[values],device_id = NODE_ID):
       response = manager.read_registers(address=addr,count=1,device_id = NODE_ID)
       logger.info(f'get max angle : {addr} ->{response[0]}')
       return response[0]
    else:
        logger.info(f'get max angle : {addr} 尝试获取最大值失败')
        return 32767

def get_max_negative_angle(manager,addr):
    values = 32768
    if manager.write_registers(address=addr,value=[values],device_id = NODE_ID):
       response = manager.read_registers(address=addr,count=1,device_id = NODE_ID)
       logger.info(f'get max negative angle : {addr} ->{response[0]}')
       return response[0]
    else:
        logger.info(f'get max negative angle : {addr} 尝试获取最大负值失败')
        return 32768

def get_min_negative_angle(manager,addr):
    values = 65535
    if manager.write_registers(address=addr,value=[values],device_id = NODE_ID):
       response = manager.read_registers(address=addr,count=1,device_id = NODE_ID)
       logger.info(f'get min negative angle : {addr} ->{response[0]}')
       return response[0]
    else:
        logger.info(f'get max negative angle : {addr} 尝试获取最小负值失败')
        return 65535

def test_read_finger_angle_target0(manager):
    print_test_info(status=TEST_START,info='read finger angle target0')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET0, count=1,device_id = NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET0}>失败,发生异常')

def test_write_finger_angle_target0(manager):
    print_test_info(status=TEST_START, info='write finger angle target0,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET0)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET0)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET0)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET0)
    # NORMAL_NEG_ANGLE= int(MIN_NEG_ANGLE + (MAX_NEG_ANGLE - MIN_NEG_ANGLE)/2)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,#32768,max negative value
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535#65535,min value
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET0, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET0, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4:
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 5:
                 assert read_response[0] == MAX_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET0}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET0, value=[FINGER_ANGLE_TARGET0],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_angle_target1(manager):
    print_test_info(status=TEST_START,info='read finger angle target1')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET1}>失败,发生异常')

def test_write_finger_angle_target1(manager):
    print_test_info(status=TEST_START, info='write finger angle target1,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET1)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET1)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET1)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET1)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET1, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET1, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4 :
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET1}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET1, value=[FINGER_ANGLE_TARGET1],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_angle_target2(manager):
    print_test_info(status=TEST_START,info='read finger angle target2')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET2}>失败,发生异常')

def test_write_finger_angle_target2(manager):
    print_test_info(status=TEST_START, info='write finger angle target2,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET2)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET2)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET2)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET2)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET2, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET2, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4 :
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET2}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET2, value=[FINGER_ANGLE_TARGET2],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_angle_target3(manager):
    print_test_info(status=TEST_START,info='read finger angle target3')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET3}>失败,发生异常')

def test_write_finger_angle_target3(manager):
    print_test_info(status=TEST_START, info='write finger angle target3,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET3)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET3)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET3)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET3)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET3, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET3, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4 :
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET3}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET3, value=[FINGER_ANGLE_TARGET3],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_angle_target4(manager):
    print_test_info(status=TEST_START,info='read finger angle target4')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET4}>失败,发生异常')

def test_write_finger_angle_target4(manager):
    print_test_info(status=TEST_START, info='write finger angle target4,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET4)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET4)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET4)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET4)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET4, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET4, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4 :
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET4}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET4, value=[FINGER_ANGLE_TARGET4],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_angle_target5(manager):
    print_test_info(status=TEST_START,info='read finger angle target5')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET5, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE_TARGET5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE_TARGET5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE_TARGET5}>失败,发生异常')

def test_write_finger_angle_target5(manager):
    print_test_info(status=TEST_START, info='write finger angle target5,The normal range is [0,65535]')
    MIN_ANGLE = get_min_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET5)
    MAX_ANGLE = get_max_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET5)
    NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
    MIN_NEG_ANGLE = get_min_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET5)
    MAX_NEG_ANGLE = get_max_negative_angle(manager=manager,addr=ROH_FINGER_ANGLE_TARGET5)
    verify_sets = [
        0,
        MIN_ANGLE,
        NORMAL_ANGLE,
        MAX_ANGLE,
        32767,#32767,max value
        32768,
        MAX_NEG_ANGLE,
        MIN_NEG_ANGLE,
        65535
    ]
    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET5, value=[value],device_id=NODE_ID)
            data = value
            read_response = manager.read_registers(address=ROH_FINGER_ANGLE_TARGET5, count=1,device_id=NODE_ID)
            if index == 0:
                assert read_response[0] == MIN_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (1,2,3):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index == 4 :
                assert read_response[0] == MAX_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            elif index in (6,7):
                assert abs(read_response[0] - data) <= FINGER_ANGLE_TARGET_MAX_LOSS,f'从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            else:
                assert read_response[0] == MIN_NEG_ANGLE,f'从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失不符合要求\n'
            logger.info(f"从寄存器{ROH_FINGER_ANGLE_TARGET5}读出的值{read_response[0]}与写入的值{data}比较，精度损失符合要求\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_ANGLE_TARGET5}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_ANGLE_TARGET5}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_ANGLE_TARGET5, value=[FINGER_ANGLE_TARGET5],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_angle0(manager):
    print_test_info(status=TEST_START,info='read finger angle0')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE0}>失败,发生异常')

def test_read_finger_angle1(manager):
    print_test_info(status=TEST_START,info='read finger angle1')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE1}>失败,发生异常')

def test_read_finger_angle2(manager):
    print_test_info(status=TEST_START,info='read finger angle2')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE2}>失败,发生异常')

def test_read_finger_angle3(manager):
    print_test_info(status=TEST_START,info='read finger angle3')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE3}>失败,发生异常')

def test_read_finger_angle4(manager):
    print_test_info(status=TEST_START,info='read finger angle4')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE4}>失败,发生异常')

def test_read_finger_angle5(manager):
    print_test_info(status=TEST_START,info='read finger angle5')
    try:
        response = manager.read_registers(address=ROH_FINGER_ANGLE5, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_ANGLE5}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_ANGLE5}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_ANGLE5}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_ANGLE5}>失败,发生异常')

def test_read_finger_force_P0(manager):
    print_test_info(status=TEST_START,info='read finger force P0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_P0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_P0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_P0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_P0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_P0}>失败,发生异常')

def test_write_finger_force_P0(manager):
    print_test_info(status=TEST_START, info='write finger force P0,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_P0, value=[value],device_id=NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P0, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P0, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_P0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_P0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_P0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_P0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_P0, value=[FINGER_FORCE_P0],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_P1(manager):
    print_test_info(status=TEST_START,info='read finger force P1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_P1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_P1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_P1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_P1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_P1}>失败,发生异常')

def test_write_finger_force_P1(manager):
    print_test_info(status=TEST_START, info='write finger force P1,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_P1, value=[value],device_id=NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P1, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P1, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_P1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_P1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_P1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_P1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_P1, value=[FINGER_FORCE_P1],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_P2(manager):
    print_test_info(status=TEST_START,info='read finger force P2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_P2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_P2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_P2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_P2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_P2}>失败,发生异常')

def test_write_finger_force_P2(manager):
    print_test_info(status=TEST_START, info='write finger force P2,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_P2, value=[value],device_id=NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P2, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P2, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_P2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_P2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_P2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_P2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_P2, value=[FINGER_FORCE_P2],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_P3(manager):
    print_test_info(status=TEST_START,info='read finger force P3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_P3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_P3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_P3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_P3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_P3}>失败,发生异常')

def test_write_finger_force_P3(manager):
    print_test_info(status=TEST_START, info='write finger force P3,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_P3, value=[value],device_id=NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P3, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P3, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_P3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_P3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_P3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_P3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_P3, value=[FINGER_FORCE_P3],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_P4(manager):
    print_test_info(status=TEST_START,info='read finger force P4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_P4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_P4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_P4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_P4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_P4}>失败,发生异常')

def test_write_finger_force_P4(manager):
    print_test_info(status=TEST_START, info='write finger force P4,The normal range is [100,50000], and the out-of-range values fall within {0,1,99,50001,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        99,# 99
        100,# 100
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_P4, value=[value],device_id=NODE_ID)
            data = value
            if index <= 2 or index >= 6 : # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P4, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_P4, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_P4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_P4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_P4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_P4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_P4, value=[FINGER_FORCE_P4],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_I0(manager):
    print_test_info(status=TEST_START,info='read finger force I0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_I0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_I0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_I0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_I0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_I0}>失败,发生异常')

def test_write_finger_force_I0(manager):
    print_test_info(status=TEST_START, info='write finger force I0,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_I0, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I0, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I0, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_I0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_I0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_I0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_I0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_I0, value=[FINGER_FORCE_I0],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_I1(manager):
    print_test_info(status=TEST_START,info='read finger force I1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_I1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_I1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_I1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_I1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_I1}>失败,发生异常')

def test_write_finger_force_I1(manager):
    print_test_info(status=TEST_START, info='write finger force I1,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_I1, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I1, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I1, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_I1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_I1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_I1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_I1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_I1, value=[FINGER_FORCE_I1])
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_I2(manager):
    print_test_info(status=TEST_START,info='read finger force I2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_I2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_I2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_I2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_I2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_I2}>失败,发生异常')

def test_write_finger_force_I2(manager):
    print_test_info(status=TEST_START, info='write finger force I2,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_I2, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I2, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I2, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_I2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_I2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_I2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_I2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_I2, value=[FINGER_FORCE_I2],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_I3(manager):
    print_test_info(status=TEST_START,info='read finger force I3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_I3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_I3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_I3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_I3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_I3}>失败,发生异常')

def test_write_finger_force_I3(manager):
    print_test_info(status=TEST_START, info='write finger force I3,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_I3, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I3, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I3, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_I3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_I3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_I3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_I3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_I3, value=[FINGER_FORCE_I3],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_I4(manager):
    print_test_info(status=TEST_START,info='read finger force I4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_I4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_I4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_I4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_I4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_I4}>失败,发生异常')

def test_write_finger_force_I4(manager):
    print_test_info(status=TEST_START, info='write finger force I4,The normal range is [0,10000], and the out-of-range values fall within {10001,65535}')
    verify_sets = [
        0,# 0
        5000,# 5000
        10000,# 10000
        10001,# 10001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_I4, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I4, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_I4, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_I4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_I4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_I4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_I4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_I4, value=[FINGER_FORCE_I4],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_D0(manager):
    print_test_info(status=TEST_START,info='read finger force D0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_D0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_D0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_D0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_D0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_D0}>失败,发生异常')

def test_write_finger_force_D0(manager):
    print_test_info(status=TEST_START, info='write finger force D0,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_D0, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D0, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D0, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_D0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_D0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_D0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_D0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_D0, value=[FINGER_FORCE_D0],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_D1(manager):
    print_test_info(status=TEST_START,info='read finger force D1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_D1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_D1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_D1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_D1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_D1}>失败,发生异常')

def test_write_finger_force_D1(manager):
    print_test_info(status=TEST_START, info='write finger force D1,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_D1, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D1, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D1, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_D1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_D1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_D1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_D1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_D1, value=[FINGER_FORCE_D1],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


def test_read_finger_force_D2(manager):
    print_test_info(status=TEST_START,info='read finger force D2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_D2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_D2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_D2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_D2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_D2}>失败,发生异常')

def test_write_finger_force_D2(manager):
    print_test_info(status=TEST_START, info='write finger force D2,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_D2, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D2, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D2, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_D2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_D2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_D2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_D2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_D2, value=[FINGER_FORCE_D2],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_D3(manager):
    print_test_info(status=TEST_START,info='read finger force D3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_D3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_D3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_D3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_D3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_D3}>失败,发生异常')

def test_write_finger_force_D3(manager):
    print_test_info(status=TEST_START, info='write finger force D3,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_D3, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D3, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D3, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_D3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_D3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_D3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_D3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_D3, value=[FINGER_FORCE_D3],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_D4(manager):
    print_test_info(status=TEST_START,info='read finger force D4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_D4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_D4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_D4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_D4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_D4}>失败,发生异常')

def test_write_finger_force_D4(manager):
    print_test_info(status=TEST_START, info='write finger force D4,The normal range is [0,50000], and the out-of-range values fall within {50001,65535}')
    verify_sets = [
        0,# 0
        25000,# 25000
        50000,# 50000
        50001,# 50001
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_D4, value=[value],device_id=NODE_ID)
            data = value
            if index > 2: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D4, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_D4, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_D4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_D4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_D4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_D4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_D4, value=[FINGER_FORCE_D4],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_G0(manager):
    print_test_info(status=TEST_START,info='read finger force G0')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_G0, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_G0}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_G0}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_G0}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_G0}>失败,发生异常')

def test_write_finger_force_G0(manager):
    print_test_info(status=TEST_START, info='write finger force G0,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_G0, value=[value],device_id=NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G0, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G0, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_G0}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_G0}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_G0}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_G0}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_G0, value=[FINGER_FORCE_G0],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_G1(manager):
    print_test_info(status=TEST_START,info='read finger force G1')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_G1, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_G1}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_G1}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_G1}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_G1}>失败,发生异常')

def test_write_finger_force_G1(manager):
    print_test_info(status=TEST_START, info='write finger force G1,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_G1, value=[value],device_id=NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G1, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G1, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_G1}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_G1}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_G1}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_G1}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_G1, value=[FINGER_FORCE_G1],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_G2(manager):
    print_test_info(status=TEST_START,info='read finger force G2')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_G2, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_G2}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_G2}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_G2}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_G2}>失败,发生异常')

def test_write_finger_force_G2(manager):
    print_test_info(status=TEST_START, info='write finger force G2,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_G2, value=[value],device_id=NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G2, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G2, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_G2}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_G2}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_G2}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_G2}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_G2, value=[FINGER_FORCE_G2],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_G3(manager):
    print_test_info(status=TEST_START,info='read finger force G3')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_G3, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_G3}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_G3}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_G3}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_G3}>失败,发生异常')

def test_write_finger_force_G3(manager):
    print_test_info(status=TEST_START, info='write finger force G3,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_G3, value=[value],device_id=NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G3, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G3, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_G3}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_G3}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_G3}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_G3}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_G3, value=[FINGER_FORCE_G3],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_G4(manager):
    print_test_info(status=TEST_START,info='read finger force G4')
    try:
        response = manager.read_registers(address=ROH_FINGER_FORCE_G4, count=1,device_id=NODE_ID)
        assert response is not None,f'读取寄存器<{ROH_FINGER_FORCE_G4}>失败'
        logger.info(f'读取寄存器<{ROH_FINGER_FORCE_G4}>成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器<{ROH_FINGER_FORCE_G4}>失败,发生异常: {e}")
        pytest.fail(f'读取寄存器<{ROH_FINGER_FORCE_G4}>失败,发生异常')



def test_write_finger_force_G4(manager):
    print_test_info(status=TEST_START, info='write finger force G4,The normal range is [1,100], and the out-of-range values fall within {0,101,65535}')
    verify_sets = [
        0,# 0
        1,# 1
        50,# 50
        100,# 100
        101,# 101
        65535# 65535
    ]

    for index,value in enumerate(verify_sets):
        try:
            response = manager.write_registers(address=ROH_FINGER_FORCE_G4, value=[value],device_id=NODE_ID)
            data = value
            if index ==0 or index > 3: # 异常值写进去不生效,底层不报错
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G4, count=1,device_id=NODE_ID)
                assert read_response[0] != data, f"超出范围的值{data}未被检测出\n"
                logger.info(f"成功检测出超出范围的值{data}\n")
            else:
                read_response = manager.read_registers(address=ROH_FINGER_FORCE_G4, count=1,device_id=NODE_ID)
                assert read_response[0] == data, f"从寄存器{ROH_FINGER_FORCE_G4}读出的值{read_response[0]}与写入的值{data}不匹配"
                logger.info(f"从寄存器{ROH_FINGER_FORCE_G4}读出的值{read_response[0]}与写入的值{data}匹配成功\n")
        except Exception as e:
                logger.error(f"写寄存器<{ROH_FINGER_FORCE_G4}>失败,发生异常: {e}")
                pytest.fail(f'写寄存器<{ROH_FINGER_FORCE_G4}>失败,发生异常')

    # 恢复默认值
    logger.info('恢复默认值')
    try:
        write_response = manager.write_registers(address=ROH_FINGER_FORCE_G4, value=[FINGER_FORCE_G4],device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")

def test_read_finger_force_ex(manager):
    print_test_info(status=TEST_START, info='read finger force ex[0~6]')
    try:
        FORCE_VALUE_LENGTH = [18, 30, 30, 30, 16, 28]
        NUM_FINGERS = 6
        FORCE_GROUP_SIZE = 100
        for i in range(NUM_FINGERS):
            reg_cnt = FORCE_VALUE_LENGTH[i]
            response = manager.read_registers(address=ROH_FINGER_FORCE_EX0+ i*FORCE_GROUP_SIZE, count=reg_cnt,device_id=NODE_ID)
            assert response is not None,f'读取寄存器<ROH_FINGER_FORCE_EX{i}>失败，读取单点力量失败'
            if len(response.registers) == reg_cnt:
                force_dot = []
                for j in range(reg_cnt):
                    force_dot.append((response.registers[j] >> 8) & 0xff)
                    force_dot.append(response.registers[j] & 0xff)
                logger.info(force_dot)
                logger.info(f'ROH_FINGER_FORCE_EX{i}成功')
    except Exception as e:
        logger.error(f"读取单点力量失败,发生异常: {e}")
        pytest.fail(f'读取单点力量失败,发生异常')

# @pytest.mark.skip('暂时跳过多个寄存器的读操作')
def test_read_multiple_holding_registers(manager):
    print_test_info(status=TEST_START,info='read multiple registers')
    try:
        response = manager.read_registers(address=ROH_FINGER_CURRENT_LIMIT0, count=6,device_id=NODE_ID)
        assert response is not None,f'读取寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>连续6个寄存器的值失败'
        logger.info(f'读取寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>连续6个寄存器的值成功,读取的值为:{response[0]}')
    except Exception as e:
        logger.error(f"读取寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>连续6个寄存器的值失败,发生异常: {e}")
        pytest.fail(f'读取寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>连续6个寄存器的值失败,发生异常')

# @pytest.mark.skip('暂时跳过多个寄存器的写操作')
def test_write_multiple_holding_registers(manager):
    print_test_info(status=TEST_START,info='write multiple registers')
    verify_sets = [600,600,# 600
                   600,600,# 600
                   600,600# 600
    ]
    try:
        response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT0, value=verify_sets,device_id=NODE_ID)
        assert response,f'写寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>,连续6个寄存器失败'
        logger.info(f'写寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>,连续6个寄存器成功')
    except Exception as e:
        logger.error(f"写寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>,连续6个寄存器失败,发生异常: {e}")
        pytest.fail(f'写寄存器起始地址<{ROH_FINGER_CURRENT_LIMIT0}>,连续6个寄存器失败,发生异常')

     # 恢复默认值
    logger.info('恢复默认值')
    try:
        default_sets = [1299,1299,# 1299
                        1299,1299,# 1299
                        1299,1299 # 1299
    ]
        write_response = manager.write_registers(address=ROH_FINGER_CURRENT_LIMIT0, value=default_sets,device_id=NODE_ID)
        assert write_response, f"恢复默认值失败\n"
        logger.info("恢复默认值成功\n")
    except Exception as e:
        logger.error(f"恢复默认值发生了异常: {e}")


# ==================== 外部调用接口 ====================
def main(ports: list = [], devices_ids: list = [], aging_duration: float = 1.5):
    test_title = 'CAN协议测试'
    global CLIENT_PORT, HAND_ID

    # 传入的完整端口名：PCAN_USBBUS1
    full_port = ports[0] if len(ports) > 0 else "COM4"

    # 给驱动使用的端口：只取最后一位数字
    CLIENT_PORT = full_port#full_port[-1]

    # 设备ID
    HAND_ID = devices_ids[0] if len(devices_ids) > 0 else 0x02

    logger.info("=" * 60)
    logger.info("        机械手 API 自动化测试启动")
    logger.info(f"        完整端口: {full_port}")
    logger.info(f"        实际使用CAN端口: {CLIENT_PORT}")
    logger.info(f"        设备ID: {hex(HAND_ID)}")
    logger.info("=" * 60)

    case_list = []

    class ResultCollector:
        def pytest_runtest_logreport(manager, report):
            if report.when == "call":
                case = report.nodeid.split("::")[-1]

                # ====================== 改成中文 ======================
                res = "通过" if report.passed else "不通过"

                err = report.longreprtext if report.failed else ""
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                case_list.append({
                    "timestamp": ts,
                    "content": case,
                    "result": res,
                    "comment": err
                })

    # 运行用例
    args = [
        "-v",
        "--tb=short",
        __file__,
    ]

    # ====================== 核心改动：只跑指定case ======================

    pytest.main(args, plugins=[ResultCollector()])

    # 返回格式：port 显示完整名称
    port_result = {
        "port": full_port,
        "gestures": case_list
    }

    logger.info("=" * 60)
    logger.info(f"测试完成，端口：{full_port}，用例数：{len(case_list)}")
    logger.info("=" * 60)

    return test_title, [port_result]


if __name__ == "__main__":
    import sys

    title, result_list = main()
    print("测试标题:", title)
    print("返回结果:", result_list)
    sys.exit(0)