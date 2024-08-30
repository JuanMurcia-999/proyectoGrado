from pysnmp.proto import api
import time, bisect
import psutil
import asyncio
import threading
import time

import socket
import psutil

cpu_values = []
diskuse = []

PROTOCOL_MODULES = {
    api.protoVersion1: api.protoModules[api.protoVersion1],
    api.protoVersion2c: api.protoModules[api.protoVersion2c],
}


def valcores():
    global cpu_values
    global diskuse
    while True:
        cpu_values = psutil.cpu_percent(percpu=True, interval=1)
        path = psutil.disk_partitions()[0][0]
        diskuse = psutil.disk_usage(path)
        time.sleep(1)


cpu_update_thread = threading.Thread(target=valcores)
cpu_update_thread.daemon = True
cpu_update_thread.start()


class General:

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __lt__(self, other):
        return self.name < other

    def __le__(self, other):
        return self.name <= other

    def __gt__(self, other):
        return self.name > other

    def __ge__(self, other):
        return self.name >= other


class SysDescr(General):
    name = (1, 3, 6, 1, 3, 100, 1, 0)

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].OctetString(
            "PySNMP example command responder"
        )


class Uptime(General):
    name = (1, 3, 6, 1, 3, 100, 2, 0)
    birthday = time.time()

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].TimeTicks((time.time() - self.birthday) * 100)


class Memorysize(General):
    name = (1, 3, 6, 1, 3, 100, 3, 0)
    mem_info = psutil.virtual_memory()

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(self.mem_info.total / (1024**2))


class Memoryused(General):
    name = (1, 3, 6, 1, 3, 100, 4, 0)
    mem_info = psutil.virtual_memory()

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(round(self.mem_info.used / (1024 ** 2)))


class CPUused(General):
    name = (1, 3, 6, 1, 3, 100, 5, 1, 0)

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(psutil.cpu_percent(interval=1))


class NumCores(General):
    name = (1, 3, 6, 1, 3, 100, 5, 2, 0)

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(psutil.cpu_count(logical=True))


class SysEntryIndex:
    name = (1, 3, 6, 1, 3, 100, 5, 2, 1)

    def __init__(self, index):
        self.index = index

    def __eq__(self, other):
        return self.name + (self.index,) == other

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(self.index)


class SysEntryValue:
    name = (1, 3, 6, 1, 3, 100, 5, 2, 2)

    def __init__(self, index):
        self.index = index

    def __eq__(self, other):
        return self.name + (self.index,) == other

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(round(cpu_values[self.index - 1]))


class DiskEntryValue:
    name = (1, 3, 6, 1, 3, 100, 6, 2, 2)

    def __init__(self, index):
        self.index = index

    def __eq__(self, other):
        return self.name + (self.index,) == other

    def __call__(self, protoVer):
        return PROTOCOL_MODULES[protoVer].Integer(
            round(diskuse[self.index - 1] / (1024**3))
        )


nucleos = psutil.cpu_count(logical=True)
cpuindex = []
cpuvalores = []
diskvalues = []

for i in range(1, nucleos + 1):
    cpuindex.append(SysEntryIndex(i))
    cpuvalores.append(SysEntryValue(i))

for i in range(1, 3):
    diskvalues.append(DiskEntryValue(i))

mibInstr = [
    SysDescr(),
    Uptime(),
    Memorysize(),
    Memoryused(),
    CPUused(),
    NumCores(),
    *cpuindex,
    *cpuvalores,
    *diskvalues,
]
