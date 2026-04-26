"""
linuxcnc_remote/__init__.py
Remote LinuxCNC API wrapper for Windows clients.
Mimics the real linuxcnc Python API, communicating with a remote proxy.
"""


from .stat import stat
from .command import command
from .error import error


# LinuxCNC mode constants (from emc.hh EMC_TASK_MODE)
MODE_MANUAL = 1
MODE_AUTO = 2
MODE_MDI = 3

# HAL constants
HAL_BIT = 1
HAL_FLOAT = 2
HAL_IN = 1
HAL_OUT = 2

 # Common command constants (from emc.hh EMC_TASK_STATE)
STATE_ESTOP = 1
STATE_ESTOP_RESET = 2
STATE_OFF = 3
STATE_ON = 4
AUTO_RUN = 1
AUTO_STEP = 2
AUTO_PAUSE = 3
AUTO_RESUME = 4
JOG_STOP = 0
JOG_CONTINUOUS = 1
JOG_INCREMENT = 2
FLOOD_ON = 1
FLOOD_OFF = 0
MIST_ON = 1
MIST_OFF = 0
SPINDLE_FORWARD = 1
SPINDLE_REVERSE = -1
SPINDLE_OFF = 0
