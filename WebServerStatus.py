import pip._vendor.requests as requests
import smtplib
from email.message import EmailMessage
import json

status = 0
with open("websitedetails.json") as f:
    jsonData = json.load(f)

WebSiteName = jsonData['WebSiteDetail']['Name']
urlAddress = jsonData['WebSiteDetail']['URL']
try:
    response = requests.get(urlAddress)
    status = response.status_code
    response.raise_for_status()
except requests.HTTPError as http_err:
    print(f'HTTP error occured: {http_err}')
except Exception as err:
    print(f'Other error occured: {err}')

# ===================================================================
# --- Sender and Reciever Email Address
# ===================================================================
cssValue = ''' table#websiteTable{
            table-layout: auto;
            width: 50%;
        }
        table, th, td{
            border: 1px solid black;
            text-align: center;
        }
        th{
            font-weight: bolder;
}'''
content = f"""
<html>
    <body>
        <style>
            {cssValue}
        </style>
        <h2 style="text-align:justify;">Website Status Info</h2>
        <div id='tableContent'>
            <table id="websiteTable">
                <tbody>
                    <tr>
                        <th>Website Name</th>
                        <th>Website URL</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>{WebSiteName}</td>
                        <td>
                            <a href="{urlAddress}" target="_blank">{urlAddress}</a>
                        </td>
                        <td style="font-weight: bolder;background-color: red;">Link is Down</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
</html>"""

sender = jsonData['sender']

#RECEVIER_EMAIL_ADDRESS IN LIST COMMA SEPARATED VALUES
recevier = jsonData['recevier']


msg = EmailMessage()
msg.set_content(content,subtype='html')

msg['From'] = sender
msg['To'] = recevier
msg['Subject'] = f"Website Status...!"

try:
    smtpobj = smtplib.SMTP(jsonData['smtp'])
    #smtpobj.sendmail(sender,recevier,message)
    if status != 200:
        smtpobj.send_message(msg)
        print("Successfully sent an Email")
except Exception:
    print ("Error: Unable to send email")
finally:
    smtpobj.quit()

