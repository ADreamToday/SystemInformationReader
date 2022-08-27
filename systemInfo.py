# -*- coding: gbk -*-
'''
@name: ϵͳ��Ϣ / SystemInfo
@author: PurePeace
@time: 2020��8��17��
@version: 0.1
'''

from typing import List, Dict, Any

import os
import time
import psutil
import platform
import hashlib
import re
import sys


from cachelib import SimpleCache
cache = SimpleCache()


UNIX: bool = os.name == 'posix'
SYS: str = platform.system()


class CpuConstants:
    def __init__(self):
        '''
        ��ʼ��CPU��������ƽ̨��

        Returns
        -------
        self.

        '''
        self.WMI = None
        self.initialed: bool = False
        self.cpuList: list = [] # windows only

        self.cpuCount: int = 0 # ����cpu����
        self.cpuCore: int = 0 # cpu����������
        self.cpuThreads: int = 0 # cpu�߼�������
        self.cpuName: str = '' # cpu�ͺ�

        self.Update(True)


    def Update(self, update: bool = False) -> None:
        '''
        ����cpu����

        Returns
        -------
        None.

        '''
        if UNIX: self.GetCpuConstantsUnix(update)
        else: self.GetCpuConstantsWindows(update)

        self.initialed: bool = True


    @property
    def getDict(self) -> Dict[int, str]:
        '''
        ���ֵ��ʽ��ȡ��ǰcpu����

        Returns
        -------
        Dict[int, str]
            DESCRIPTION.

        '''
        if not self.initialed: self.Update()
        return {
            'cpu_count': self.cpuCount,
            'cpu_name': self.cpuName,
            'cpu_core': self.cpuCore,
            'cpu_threads': self.cpuThreads
        }


    def GetCpuConstantsUnix(self, update: bool = False) -> None:
        '''
        ��ȡunix�µ�cpu��Ϣ

        Parameters
        ----------
        update : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None
            DESCRIPTION.

        '''
        if update or not self.initialed:
            ids: list = re.findall("physical id.+", readFile('/proc/cpuinfo'))

            # ����cpu����
            self.cpuCount: int = len(set(ids))

            # cpu�ͺţ����ƣ�
            self.cpuName: str = self.getCpuTypeUnix()


            self.GetCpuConstantsBoth()


    def InitWmi(self) -> None:
        '''
        ��ʼ��wmi��for windows��

        Returns
        -------
        None
            DESCRIPTION.

        '''
        import wmi
        self.WMI = wmi.WMI()


    def GetCpuConstantsBoth(self, update: bool = False) -> None:
        '''
        ��ȡ��ƽ̨���õ�cpu��Ϣ

        Parameters
        ----------
        update : bool, optional
            ǿ�Ƹ�������. The default is False.

        Returns
        -------
        None
            DESCRIPTION.

        '''
        if update or not self.initialed:

            # cpu�߼�������
            self.cpuThreads: int = psutil.cpu_count()

            # cpu����������
            self.cpuCore: int = psutil.cpu_count(logical=False)


    def GetCpuConstantsWindows(self, update: bool = False) -> None:
        '''
        ��ȡwindowsƽ̨��cpu��Ϣ

        Parameters
        ----------
        update : bool, optional
            ǿ�Ƹ�������. The default is False.

        Returns
        -------
        None
            DESCRIPTION.

        '''
        if update or not self.initialed:

            # ��ʼ��wmi
            if self.WMI == None: self.InitWmi()

            # cpu�б�
            self.cpuList: list = self.WMI.Win32_Processor()

            # ����cpu����
            self.cpuCount: int = len(self.cpuList)

            # cpu�ͺţ����ƣ�
            self.cpuName: str = self.cpuList[0].Name


            self.GetCpuConstantsBoth()


    @staticmethod
    def getCpuTypeUnix() -> str:
        '''
        ��ȡCPU�ͺţ�unix��

        Returns
        -------
        str
            CPU�ͺ�.

        '''
        cpuinfo: str = readFile('/proc/cpuinfo')
        rep: str = 'model\s+name\s+:\s+(.+)'
        tmp = re.search(rep,cpuinfo,re.I)
        cpuType: str = ''
        if tmp:
            cpuType: str = tmp.groups()[0]
        else:
            cpuinfo = ExecShellUnix('LANG="en_US.UTF-8" && lscpu')[0]
            rep = 'Model\s+name:\s+(.+)'
            tmp = re.search(rep,cpuinfo,re.I)
            if tmp: cpuType = tmp.groups()[0]
        return cpuType


def GetCpuInfo(interval: int = 1) -> Dict[str, Any]:
    '''
    ��ȡCPU��Ϣ

    Parameters
    ----------
    interval : int, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    Dict[float, list, dict]
        DESCRIPTION.

    '''
    time.sleep(0.5)


    # cpu��ʹ����
    used: float = psutil.cpu_percent(interval)

    # ÿ���߼�cpuʹ����
    usedList: List[float] = psutil.cpu_percent(percpu=True)


    return {'used': used, 'used_list': usedList, **cpuConstants.getDict}


def readFile(filename: str) -> str:
    '''
    ��ȡ�ļ�����

    Parameters
    ----------
    filename : str
        �ļ���.

    Returns
    -------
    str
        �ļ�����.

    '''
    try:
        with open(filename, 'r', encoding='utf-8') as file: return file.read()
    except:
        pass

    return ''


def GetLoadAverage() -> dict:
    '''
    ��ȡ����������״̬����ƽ̨��

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    try: c: list = os.getloadavg()
    except: c: list = [0,0,0]
    data: dict = {i: c[idx] for idx, i in enumerate(('one', 'five', 'fifteen'))}
    data['max'] = psutil.cpu_count() * 2
    data['limit'] = data['max']
    data['safe'] = data['max'] * 0.75
    return data


def GetMemInfo() -> dict:
    '''
    ��ȡ�ڴ���Ϣ����ƽ̨��

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    if UNIX: return GetMemInfoUnix()
    return GetMemInfoWindows()


def GetMemInfoUnix() -> Dict[str, int]:
    '''
    ��ȡ�ڴ���Ϣ��unix��

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    mem = psutil.virtual_memory()
    memInfo: dict = {
        'memTotal': ToSizeInt(mem.total, 'MB'),
        'memFree': ToSizeInt(mem.free, 'MB'),
        'memBuffers': ToSizeInt(mem.buffers, 'MB'),
        'memCached': ToSizeInt(mem.cached, 'MB'),
    }
    memInfo['memRealUsed'] = \
        memInfo['memTotal'] - \
        memInfo['memFree'] - \
        memInfo['memBuffers'] - \
        memInfo['memCached']

    memInfo['memUsedPercent'] = memInfo['memRealUsed'] / memInfo['memTotal'] * 100

    return memInfo


def GetMemInfoWindows() -> dict:
    '''
    ��ȡ�ڴ���Ϣ��windows��

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    mem = psutil.virtual_memory()
    memInfo: dict = {
        'memTotal': ToSizeInt(mem.total, 'MB'),
        'memFree': ToSizeInt(mem.free, 'MB'),
        'memRealUsed': ToSizeInt(mem.used, 'MB'),
        'menUsedPercent': mem.used / mem.total * 100
    }

    return memInfo


def ToSizeInt(byte: int, target: str) -> int:
    '''
    ���ֽڴ�Сת��ΪĿ�굥λ�Ĵ�С

    Parameters
    ----------
    byte : int
        int��ʽ���ֽڴ�С��bytes size��
    target : str
        Ŀ�굥λ��str.

    Returns
    -------
    int
        ת��ΪĿ�굥λ����ֽڴ�С.

    '''
    return int(byte/1024**(('KB','MB','GB','TB').index(target) + 1))


def ToSizeString(byte: int) -> str:
    '''
    ��ȡ�ֽڴ�С�ַ���

    Parameters
    ----------
    byte : int
        int��ʽ���ֽڴ�С��bytes size��.

    Returns
    -------
    str
        �Զ�ת����Ĵ�С�ַ������磺6.90 GB.

    '''
    units: tuple = ('b','KB','MB','GB','TB')
    re = lambda: '{:.2f} {}'.format(byte, u)
    for u in units:
        if byte < 1024: return re()
        byte /= 1024
    return re()


def GetDiskInfo() -> list:
    '''
    ��ȡ������Ϣ����ƽ̨��

    Returns
    -------
    list
        �б�.

    '''
    try:
        if UNIX: return GetDiskInfoUnix()
        return GetDiskInfoWindows()
    except Exception as err:
        print('��ȡ������Ϣ�쳣��unix: {}����'.format(UNIX), err)
        return []


def GetDiskInfoWindows() -> list:
    '''
    ��ȡ������ϢWindows

    Returns
    -------
    diskInfo : list
        �б�.

    '''
    diskIo: list = psutil.disk_partitions()
    diskInfo: list = []
    for disk in diskIo:
        tmp: dict = {}
        try:
            tmp['path'] = disk.mountpoint.replace("\\","/")
            usage = psutil.disk_usage(disk.mountpoint)
            tmp['size'] = {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
            tmp['fstype'] = disk.fstype
            tmp['inodes'] = False
            diskInfo.append(tmp)
        except:
            pass
    return diskInfo


def GetDiskInfoUnix() -> list:
     '''
    ��ȡӲ�̷�����Ϣ��unix��

    Returns
    -------
    list
        DESCRIPTION.

    '''
     temp: list = (
         ExecShellUnix("df -h -P|grep '/'|grep -v tmpfs")[0]).split('\n')
     tempInodes: list = (
         ExecShellUnix("df -i -P|grep '/'|grep -v tmpfs")[0]).split('\n')
     diskInfo: list = []
     n: int = 0
     cuts: list = [
         '/mnt/cdrom',
         '/boot',
         '/boot/efi',
         '/dev',
         '/dev/shm',
         '/run/lock',
         '/run',
         '/run/shm',
         '/run/user'
     ]
     for tmp in temp:
         n += 1
         try:
             inodes: list = tempInodes[n-1].split()
             disk: list = tmp.split()
             if len(disk) < 5: continue
             if disk[1].find('M') != -1: continue
             if disk[1].find('K') != -1: continue
             if len(disk[5].split('/')) > 10: continue
             if disk[5] in cuts: continue
             if disk[5].find('docker') != -1: continue
             arr = {}
             arr['path'] = disk[5]
             tmp1 = [disk[1],disk[2],disk[3],disk[4]]
             arr['size'] = tmp1
             arr['inodes'] = [inodes[1],inodes[2],inodes[3],inodes[4]]
             diskInfo.append(arr)
         except Exception as ex:
             print('��Ϣ��ȡ����', str(ex))
             continue
     return diskInfo



def md5(strings: str) -> str:
    '''
    ����md5

    Parameters
    ----------
    strings : TYPE
        Ҫ����hash�������ַ���

    Returns
    -------
    str[32]
        hash����ַ���.

    '''

    m = hashlib.md5()
    m.update(strings.encode('utf-8'))
    return m.hexdigest()


def GetErrorInfo() -> str:
    '''
    ��ȡtraceback�еĴ���

    Returns
    -------
    str
        DESCRIPTION.

    '''
    import traceback
    errorMsg = traceback.format_exc()
    return errorMsg


def ExecShellUnix(cmdstring: str, shell=True):
    '''
    ִ��Shell���Unix��

    Parameters
    ----------
    cmdstring : str
        DESCRIPTION.
    shell : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    a : TYPE
        DESCRIPTION.
    e : TYPE
        DESCRIPTION.

    '''
    a: str = ''
    e: str = ''
    import subprocess,tempfile

    try:
        rx: str = md5(cmdstring)
        succ_f = tempfile.SpooledTemporaryFile(
            max_size = 4096,
            mode = 'wb+',
            suffix = '_succ',
            prefix = 'btex_' + rx ,
            dir = '/dev/shm'
        )
        err_f = tempfile.SpooledTemporaryFile(
            max_size = 4096,
            mode = 'wb+',
            suffix = '_err',
            prefix = 'btex_' + rx ,
            dir = '/dev/shm'
        )
        sub = subprocess.Popen(
            cmdstring,
            close_fds = True,
            shell = shell,
            bufsize = 128,
            stdout = succ_f,
            stderr = err_f
        )
        sub.wait()
        err_f.seek(0)
        succ_f.seek(0)
        a = succ_f.read()
        e = err_f.read()
        if not err_f.closed: err_f.close()
        if not succ_f.closed: succ_f.close()
    except Exception as err:
        print(err)
    try:
        if type(a) == bytes: a = a.decode('utf-8')
        if type(e) == bytes: e = e.decode('utf-8')
    except Exception as err:
        print(err)

    return a,e


def GetNetWork() -> dict:
    '''
    ��ȡϵͳ������Ϣ

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    networkIo: list = [0,0,0,0]
    cache_timeout: int = 86400
    try:
        networkIo = psutil.net_io_counters()[:4]
    except:
        pass

    otime = cache.get("otime")
    if not otime:
        otime = time.time()
        cache.set('up',networkIo[0],cache_timeout)
        cache.set('down',networkIo[1],cache_timeout)
        cache.set('otime',otime ,cache_timeout)

    ntime = time.time()
    networkInfo: dict = {'up': 0, 'down': 0}
    networkInfo['upTotal']   = networkIo[0]
    networkInfo['downTotal'] = networkIo[1]
    try:
        networkInfo['up'] = round(
            float(networkIo[0] - cache.get("up")) / 1024 / (ntime - otime),
            2
        )
        networkInfo['down'] = round(
            float(networkIo[1] - cache.get("down")) / 1024 / (ntime -  otime),
            2
        )
    except:
        pass

    networkInfo['downPackets'] = networkIo[3]
    networkInfo['upPackets'] = networkIo[2]

    cache.set('up',networkIo[0],cache_timeout)
    cache.set('down',networkIo[1],cache_timeout)
    cache.set('otime', time.time(),cache_timeout)

    return networkInfo


def GetSystemInfo() -> dict:
    systemInfo: dict = {}
    systemInfo['cpu'] = GetCpuInfo()
    systemInfo['load'] = GetLoadAverage()
    systemInfo['mem'] = GetMemInfo()
    systemInfo['disk'] = GetDiskInfo()

    return systemInfo



def GetIoReadWrite() -> Dict[str, int]:
    '''
    ��ȡϵͳIO��д

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    ioDisk = psutil.disk_io_counters()
    ioTotal: dict = {}
    ioTotal['write'] = GetIoWrite(ioDisk.write_bytes)
    ioTotal['read'] = GetIoRead(ioDisk.read_bytes)
    return ioTotal


def GetIoWrite(ioWrite: int) -> int:
    '''
    ��ȡIOд

    Parameters
    ----------
    ioWrite : TYPE
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    '''
    diskWrite: int = 0
    oldWrite: int = cache.get('io_write')
    if not oldWrite:
        cache.set('io_write', ioWrite)
        return diskWrite;

    oldTime: float = cache.get('io_time')
    newTime: float = time.time()
    if not oldTime: oldTime = newTime
    ioEnd: int = (ioWrite - oldWrite)
    timeEnd: float = (time.time() - oldTime)
    if ioEnd > 0:
        if timeEnd < 1: timeEnd = 1
        diskWrite = ioEnd / timeEnd
    cache.set('io_write',ioWrite)
    cache.set('io_time',newTime)
    if diskWrite > 0: return int(diskWrite)
    return 0


def GetIoRead(ioRead):
    '''
    ��ȡIO��

    Parameters
    ----------
    ioRead : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    diskRead: int = 0
    oldRead: int = cache.get('io_read')
    if not oldRead:
        cache.set('io_read',ioRead)
        return diskRead;
    oldTime: float = cache.get('io_time')
    newTime: float = time.time()
    if not oldTime: oldTime = newTime
    ioEnd: int = (ioRead - oldRead)
    timeEnd: float = (time.time() - oldTime)
    if ioEnd > 0:
        if timeEnd < 1: timeEnd = 1;
        diskRead = ioEnd / timeEnd;
    cache.set('io_read', ioRead)
    if diskRead > 0: return int(diskRead)
    return 0


def GetRegValue(key: str, subkey: str, value: str) -> Any:
    '''
    ��ȡϵͳע�����Ϣ

    Parameters
    ----------
    key : str
        ����.
    subkey : str
        ·��.
    value : str
        key.

    Returns
    -------
    value : Any
        DESCRIPTION.

    '''
    import winreg
    key = getattr(winreg, key)
    handle = winreg.OpenKey(key, subkey)
    (value, type) = winreg.QueryValueEx(handle, value)
    return value


def GetSystemVersion() -> str:
    '''
    ��ȡ����ϵͳ�汾����ƽ̨��

    Returns
    -------
    str
        DESCRIPTION.

    '''
    if UNIX: return GetSystemVersionUnix()
    return GetSystemVersionWindows()


def GetSystemVersionWindows() -> str:
    '''
    ��ȡ����ϵͳ�汾��windows��

    Returns
    -------
    str
        DESCRIPTION.

    '''
    try:
        import platform
        bit: str = 'x86';
        if 'PROGRAMFILES(X86)' in os.environ: bit = 'x64'

        def get(key: str):
            return GetRegValue(
                "HKEY_LOCAL_MACHINE",
                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                key
            )

        osName = get('ProductName')
        build = get('CurrentBuildNumber')

        version: str = '{} (build {}) {} (Py{})'.format(
            osName, build, bit, platform.python_version())
        return version
    except Exception as ex:
        print('��ȡϵͳ�汾ʧ�ܣ�����' + str(ex))
        return 'δ֪ϵͳ�汾.'


def GetSystemVersionUnix() -> str:
    '''
    ��ȡϵͳ�汾��unix��

    Returns
    -------
    str
        ϵͳ�汾.

    '''
    try:
        version: str = readFile('/etc/redhat-release')
        if not version:
            version = readFile(
                '/etc/issue'
            ).strip().split("\n")[0].replace('\\n','').replace('\l','').strip()
        else:
            version = version.replace(
                'release ',''
            ).replace('Linux','').replace('(Core)','').strip()
        v = sys.version_info
        return version + '(Py {}.{}.{})'.format(v.major, v.minor, v.micro)
    except Exception as err:
        print('��ȡϵͳ�汾ʧ�ܣ�����', err)
        return 'δ֪ϵͳ�汾.'


def GetBootTime() -> dict:
    '''
    ��ȡ��ǰϵͳ����ʱ��

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    bootTime: float = psutil.boot_time()
    return {
        'timestamp': bootTime,
        'runtime': time.time() - bootTime,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    }


def GetCpuConstants() -> dict:
    '''
    ��ȡCPU������Ϣ

    Parameters
    ----------
    cpuConstants : CpuConstants
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    return cpuConstants.getDict


def GetFullSystemData() -> dict:
    '''
    ��ȡ��ȫ��ϵͳ��Ϣ

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    systemData: dict = {
        **GetSystemInfo(),
        'network': { **GetNetWork() },
        'io': { **GetIoReadWrite() },
        'boot': { **GetBootTime() },
        'time': time.time()
    }
    return systemData

cpuConstants = CpuConstants()

if __name__ == '__main__':
    print(GetFullSystemData())
    print(GetCpuConstants())
    print(GetSystemInfo())
    print(GetNetWork())
    print(GetIoReadWrite())
    