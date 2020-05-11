import psutil
import time
import os
import smtplib
from email.message import EmailMessage

# ===================================================================
# --- OS constants
# ===================================================================

WINDOWS = os.name == "nt"

def _total_cpu_time(cputimes):
    totalCPUTime = 0.0
    for cputime in cputimes:
        totalCPUTime += cputime
    return totalCPUTime

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

# ===================================================================
# --- Sender and Reciever Email Address
# ===================================================================

sender = '<<SENDER_EMAIL_ADDRESS>>'
recevier = [] #RECEVIER_EMAIL_ADDRESS IN LIST COMMA SEPARATED VALUES

# ===================================================================
# --- Process Constants
# ===================================================================

PROCESS_NAME = "<<Process_Name>>"
PROCESS_THERSHOLD_LIMIT = 70 #In mb's

processDetails = process_info_by_name(PROCESS_NAME)
if len(processDetails) !=0 and len(processDetails) == 1:
    processDetail = processDetails[0]
    processName = processDetail['Name']
    processId = processDetail['PID']
    processCPU = round(processDetail['CPU(S)'], 2)
    processNPM = round(processDetail['NPM(K)'] / 1024,2)
    processWS = round(processDetail['WS(K)'] / 1024,2)
    processPM = round(processDetail['PM(K)'] / 1024, 2)
    processHandles = processDetail['Handles']
    processPath = processDetail['cmdline']
    processCreatedDTM = processDetail['CreatedDTM']

# ===================================================================
# --- HTMl and CSS Constants
# ===================================================================

cssValue = '''table, th, td {
  border: 1px solid black;
}'''
content = f"""<html>
<body>
<style>
{cssValue}
</style>
<h2 style="text-align:center">Process Utilization Info</h2>
<table style="width:50%">
  <tr>
    <th>Name</th>
    <th>PID</th> 
    <th>CPU(s)</th>
    <th>NPM(mb)</th>
    <th>PM(mb)</th>
    <th>WS(mb)</th>
    <th>Process Path</th>
    <th>CreatedDTM</th>
  </tr>
  <tr>
    <td>{processName}</td>
    <td>{processId}</td>
    <td>{processCPU}</td>
    <td>{processNPM}</td>
    <td style="background-color:#FF0000">{processPM}</td>
    <td>{processWS}</td>
    <td>{processPath}</td>
    <td>{processCreatedDTM}</td>
  </tr>
</table>
</body>
</html>"""


msg = EmailMessage()
msg.set_content(content,subtype='html')

msg['Subject'] = f"Memory Uitlization of {processDetails[0]['Name']} Process"
msg['From'] = sender
msg['To'] = recevier

try:
    smtpobj = smtplib.SMTP('<<SMTP_IP_ADDRESS>>')
    #smtpobj.sendmail(sender,recevier,message)
    if processPM > PROCESS_THERSHOLD_LIMIT and processPM != 0.00:
        smtpobj.send_message(msg)
        print("Successfully sent an Email")
except Exception:
    print ("Error: Unable to send email")
finally:
    smtpobj.quit()