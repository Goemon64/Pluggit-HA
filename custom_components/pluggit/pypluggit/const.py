"""Const for pypluggit."""

from enum import Enum, IntEnum, auto

from pymodbus.client import ModbusTcpClient as m


class Register(Enum):
    """Name registers."""

    PRM_SYSTEM_ID = auto()
    PRM_SYSTEM_SERIAL_NUM_LOW = auto()
    PRM_SYSTEM_SERIAL_NUM_HIGH = auto()
    PRM_FW_VERSION = auto()
    PRM_DATE_TIME = auto()
    PRM_DATE_TIME_SET = auto()
    PRM_WORK_TIME = auto()
    PRM_CURRENT_BL_STATE = auto()
    PRM_RAM_IDX_UNIT_MODE = auto()
    PRM_ROM_IDX_SPEED_LEVEL = auto()
    PRM_HAL_TAHO_1 = auto()
    PRM_HAL_TAHO_2 = auto()
    PRM_RAM_IDX_T1 = auto()
    PRM_RAM_IDX_T2 = auto()
    PRM_RAM_IDX_T3 = auto()
    PRM_RAM_IDX_T4 = auto()
    PRM_FILTER_REMAINING_TIME = auto()
    PRM_FILTER_DEFAULT_TIME = auto()
    PRM_FILTER_RESET = auto()
    PRM_FILTER_DIRTINESS_DEGREE = auto()
    PRM_BYPASS_TMIN = auto()
    PRM_BYPASS_TMAX = auto()
    PRM_RAM_IDX_BYPASS_ACTUAL_STATE = auto()
    PRM_RAM_IDX_BYPASS_MANUAL_TIMEOUT = auto()
    PRM_BYPASS_TMIN_SUMMER = auto()
    PRM_BYPASS_TMAX_SUMMER = auto()
    PRM_NUM_OF_WEEK_PROGRAM = auto()
    PRM_NIGHT_MODE_STATE = auto()
    PRM_ROM_IDX_NIGHT_MODE_START_HOUR = auto()
    PRM_ROM_IDX_NIGHT_MODE_START_MIN = auto()
    PRM_ROM_IDX_NIGHT_MODE_END_HOUR = auto()
    PRM_ROM_IDX_NIGHT_MODE_END_MIN = auto()
    PRM_VOC = auto()
    PRM_RAM_IDX_RH3_CORRECTED = auto()
    PRM_LAST_ACTIVE_ALARM = auto()
    PRM_SET_ALARM_NUM = auto()


class Component(Enum):
    """Possible components for pluggit."""

    FP1 = 0x0001
    WEEK = 0x0002
    BYPASS = 0x0004
    LRSWITCH = 0x0008
    INTERNAL_PREHEATER = 0x0010
    SERVO_FLOW = 0x0020
    RH_SENSOR = 0x0040
    VOC_SENSOR = 0x0080
    EXT_OVERRIDE = 0x0100
    HAC1 = 0x0200
    HRC2 = 0x0400
    PC_TOOL = 0x0800
    APPS = 0x1000
    ZEEGBEE = 0x2000
    DI1_OVERRIDE = 0x4000
    DI2_OVERRIDE = 0x8000


class ActiveUnitMode(Enum):
    """Active unit mode."""

    DEMAND_MODE = 0x0002
    MANUAL_MODE = 0x0004
    WEEK_PROGRAM_MODE = 0x0008
    AWAY_MODE = 0x0010
    FIREPLACE_MODE = 0x0040
    SUMMER_MODE = 0x0800
    NIGHT_MODE = 0x0020
    END_AWAY_MODE = 0x8010
    END_FIREPLACE_MODE = 0x8040
    END_SUMMER_MODE = 0x8800
    END_NIGHT_MODE = 0x8020
    SELECT_MANUAL_BYPASS = 0x0080
    DESELECT_MANUAL_BYPASS = 0x8080


class SpeedLevelFan(Enum):
    """Speed level."""

    LEVEL_0 = 0x0000
    LEVEL_1 = 0x0001
    LEVEL_2 = 0x0002
    LEVEL_3 = 0x0003
    LEVEL_4 = 0x0004


class WeekProgram(Enum):
    """Week program."""

    PROGRAM_1 = 0x0000
    PROGRAM_2 = 0x0001
    PROGRAM_3 = 0x0002
    PROGRAM_4 = 0x0003
    PROGRAM_5 = 0x0004
    PROGRAM_6 = 0x0005
    PROGRAM_7 = 0x0006
    PROGRAM_8 = 0x0007
    PROGRAM_9 = 0x0008
    PROGRAM_10 = 0x0009
    PROGRAM_11 = 0x000A


class Alarm(IntEnum):
    """Alarms."""

    NONE = 0
    EXHAUST_FAN_ALARM = 1
    SUPPLY_FAN_ALARM = 2
    BYPASS_ALARM = 3
    T1_ALARM = 4
    T2_ALARM = 5
    T3_ALARM = 6
    T4_ALARM = 7
    T5_ALARM = 8
    RH_ALARM = 9
    OUTDOOR13_ALARM = 10
    SUPPLY_5_ALARM = 11
    FIRE_ALARM = 12
    COMMUNICATION_ALARM = 13
    FIRETERMONSTAT_ALARM = 14
    HIGH_WATERLEVEL_ALARM = 15


DEVICE_TYPE = {1: "AP190", 2: "AP310", 3: "AP460", 4: "AD160"}

CURRENT_UNIT_MODE = {
    0: "Standby",
    1: "Manual",
    2: "Demand",
    3: "Week Program",
    4: "Servo-flow",
    5: "Away",
    6: "Summer",
    7: "DI Override",
    8: "Hygrostat Override",
    9: "Fireplace",
    10: "Installer",
    11: "Fail Safe 1",
    12: "Fail Safe 2",
    13: "Fail Off",
    14: "Defrost Off",
    15: "Defrost",
    16: "Night",
}

DEGREE_OF_DIRTINESS = {
    0: "0 - 33%",
    1: "34 - 67%",
    2: "68 - 99%",
    3: "100%",
}

BYPASS_STATE = {
    0: "Closed",
    1: "In Process",
    32: "Closing",
    64: "Opening",
    255: "Opened",
}

REGISTER_DIC = {
    Register.PRM_SYSTEM_ID: [2, m.DATATYPE.UINT32],
    Register.PRM_SYSTEM_SERIAL_NUM_LOW: [4, m.DATATYPE.UINT32],
    Register.PRM_SYSTEM_SERIAL_NUM_HIGH: [6, m.DATATYPE.UINT32],
    Register.PRM_FW_VERSION: [24, m.DATATYPE.UINT32],
    Register.PRM_DATE_TIME: [108, m.DATATYPE.UINT32],
    Register.PRM_DATE_TIME_SET: [110, m.DATATYPE.UINT32],
    Register.PRM_WORK_TIME: [624, m.DATATYPE.UINT32],
    Register.PRM_CURRENT_BL_STATE: [472, m.DATATYPE.UINT32],
    Register.PRM_RAM_IDX_UNIT_MODE: [168, m.DATATYPE.UINT32],
    Register.PRM_ROM_IDX_SPEED_LEVEL: [324, m.DATATYPE.UINT32],
    Register.PRM_RAM_IDX_T1: [132, m.DATATYPE.FLOAT32],
    Register.PRM_RAM_IDX_T2: [134, m.DATATYPE.FLOAT32],
    Register.PRM_RAM_IDX_T3: [136, m.DATATYPE.FLOAT32],
    Register.PRM_RAM_IDX_T4: [138, m.DATATYPE.FLOAT32],
    Register.PRM_FILTER_REMAINING_TIME: [554, m.DATATYPE.UINT32],
    Register.PRM_FILTER_DEFAULT_TIME: [556, m.DATATYPE.UINT32],
    Register.PRM_FILTER_RESET: [558, m.DATATYPE.UINT32],
    Register.PRM_FILTER_DIRTINESS_DEGREE: [612, m.DATATYPE.UINT32],
    Register.PRM_BYPASS_TMIN: [444, m.DATATYPE.FLOAT32],
    Register.PRM_BYPASS_TMAX: [446, m.DATATYPE.FLOAT32],
    Register.PRM_RAM_IDX_BYPASS_ACTUAL_STATE: [198, m.DATATYPE.UINT32],
    Register.PRM_RAM_IDX_BYPASS_MANUAL_TIMEOUT: [264, m.DATATYPE.UINT32],
    Register.PRM_BYPASS_TMIN_SUMMER: [766, m.DATATYPE.FLOAT32],
    Register.PRM_BYPASS_TMAX_SUMMER: [764, m.DATATYPE.FLOAT32],
    Register.PRM_NUM_OF_WEEK_PROGRAM: [466, m.DATATYPE.UINT32],
    Register.PRM_RAM_IDX_RH3_CORRECTED: [196, m.DATATYPE.UINT32],
    Register.PRM_VOC: [430, m.DATATYPE.UINT32],
    Register.PRM_HAL_TAHO_1: [100, m.DATATYPE.FLOAT32],
    Register.PRM_HAL_TAHO_2: [102, m.DATATYPE.FLOAT32],
    Register.PRM_ROM_IDX_NIGHT_MODE_START_HOUR: [332, m.DATATYPE.UINT32],
    Register.PRM_ROM_IDX_NIGHT_MODE_START_MIN: [334, m.DATATYPE.UINT32],
    Register.PRM_ROM_IDX_NIGHT_MODE_END_HOUR: [336, m.DATATYPE.UINT32],
    Register.PRM_ROM_IDX_NIGHT_MODE_END_MIN: [338, m.DATATYPE.UINT32],
    Register.PRM_NIGHT_MODE_STATE: [560, m.DATATYPE.UINT32],
    Register.PRM_LAST_ACTIVE_ALARM: [516, m.DATATYPE.UINT32],
    Register.PRM_SET_ALARM_NUM: [514, m.DATATYPE.UINT32],
}
