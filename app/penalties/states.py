from enum import Enum

class PenaltyState(Enum):
    NORMAL = "NORMAL"
    WARN = "WARN"
    THROTTLE = "THROTTLE"
    TEMP_BLOCK = "TEMP_BLOCK"
    BLOCK = "BLOCK"