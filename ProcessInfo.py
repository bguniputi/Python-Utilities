import psutil
import time
import os

# ===================================================================
# --- OS constants
# ===================================================================

WINDOWS = os.name == "nt"

def getSortedProcessNamesWithPID():
    processDict = {}
    for proc in psutil.process_iter():
        try:
            processDict[proc.name()] = proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    sortedDict = {}
    for key in sorted(processDict.keys()):
        sortedDict[key] = processDict[key]

    return sortedDict


def process_info():
    
    listOfProcessNames = []
    try:
        for proc in psutil.process_iter():
            with proc.oneshot():
                mem = proc.memory_info()
                info = proc.as_dict(['pid','name', 'status', 'username', 'cpu_times', 
                                                'num_handles','cmdline','create_time'])
                rss = (mem.rss / 1024)
                vms = (mem.vms / 1024)
                nonpaged_pool = (mem.nonpaged_pool / 1024)
                cputime = _total_cpu_time(info["cpu_times"])
                localtime = time.strftime(
                    "%Y%m%d%H%M%S", time.localtime(info["create_time"]))

                dict = {"Name": proc.name(),
                        "PID": info["pid"],
                        "UserName": info["username"],
                        "WS(K)": rss,
                        "PM(K)": vms,
                        "NPM(K)": nonpaged_pool,
                        "Handles": info["num_handles"],
                        "CPU(S)": cputime,
                        "cmdline": info["cmdline"][0],
                        "CreatedDTM": localtime}
                
                listOfProcessNames.append(dict)
    except psutil.Error as error:
        print(error.msg)

    return listOfProcessNames


def process_info_by_name(name):
    
    processInfoList = []
    if  WINDOWS:
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() == name.lower():
                    with proc.oneshot():
                        mem = proc.memory_info()
                        info = proc.as_dict(["pid", "status", "num_handles",
                                            "username", "cmdline", "create_time", "cpu_times"])
                else:
                    continue
            except psutil.AccessDenied:
                pass
            except psutil.NoSuchProcess:
                pass
            else:
                rss = (mem.rss / 1024)
                vms = (mem.vms / 1024)
                nonpaged_pool = (mem.nonpaged_pool / 1024)
                cputime = _total_cpu_time(info["cpu_times"])
                localtime = time.strftime(
                    "%Y%m%d%H%M%S", time.localtime(info["create_time"]))

                dict = {"Name": proc.name(),
                        "PID": info["pid"],
                        "UserName": info["username"],
                        "WS(K)": rss,
                        "PM(K)": vms,
                        "NPM(K)": nonpaged_pool,
                        "Handles": info["num_handles"],
                        "CPU(S)": cputime,
                        "cmdline": info["cmdline"][0],
                        "CreatedDTM": localtime}

                processInfoList.append(dict)
        if len(processInfoList) != 0:
            return processInfoList
        else:
            print("No Such Process Exists by name: {} in the system".format(name))
    else:
        print("Not implented for Linux, OSX and any other OS!")


def process_info_by_pid(pid):

    if WINDOWS:
        for proc in psutil.process_iter():
            try:
                if proc.pid == pid:
                    with proc.oneshot():
                        mem = proc.memory_info()
                        info = proc.as_dict(["pid", "status", "num_handles",
                                            "username", "cmdline", "create_time", "cpu_times"])
                else:
                    continue
            except psutil.AccessDenied:
                pass
            except psutil.NoSuchProcess:
                pass
            else:
                rss = (mem.rss / 1024)
                vms = (mem.vms / 1024)
                nonpaged_pool = (mem.nonpaged_pool / 1024)
                cputime = _total_cpu_time(info["cpu_times"])
                localtime = time.strftime(
                    "%Y%m%d%H%M%S", time.localtime(info["create_time"]))

                dict = {"Name": proc.name(),
                        "PID": info["pid"],
                        "UserName": info["username"],
                        "WS(K)": rss,
                        "PM(K)": vms,
                        "NPM(K)": nonpaged_pool,
                        "Handles": info["num_handles"],
                        "CPU(S)": cputime,
                        "cmdline": info["cmdline"][0],
                        "CreatedDTM": localtime}

        if len(dict) != 0:
            return dict
        else:
            print("No Such Process Exists by PID: {} in the system" %(pid))
    else:
        print("Not implented for Linux, OSX and any other OS!")

def _total_cpu_time(cputimes):
    totalCPUTime = 0.0
    for cputime in cputimes:
        totalCPUTime += cputime
    return totalCPUTime

def process_id_by_name(name):
    processId = 0
    for proc in psutil.process_iter(['pid','name']):        
        try:
            if proc.name().lower() == name.lower():
                processId = proc.info['pid']
        except psutil.AccessDenied:
            pass
    return processId

def kill_process(pid, timeOut=None):

    try:
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeOut)
    except psutil.NoSuchProcess:
        print("No Such Process Exists {}".format(pid))
    except psutil.AccessDenied:
        print("Access Denied or no rights to kill the process")
    except psutil.TimeoutExpired:
        print("TimeOut and process is still alive")

def kill_process_by_name(name):
    processDetails = process_info_by_name(name)
    for processDetail in processDetails:
        processPID = processDetail["PID"]
        kill_process(processPID)

if __name__ == "__main__":
    print(process_info())