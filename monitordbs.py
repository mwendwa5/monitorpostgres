#!/usr/bin/python

import psycopg2
import smtplib
import datetime
import email
import tempfile
import pexpect
import time
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser
import sys
import requests
import json
server = smtplib.SMTP_SSL('smtp.mydomain.com',465)
fromaddr = "alerts@mydomain.com"
my_pass = myemailpassword"
toaddr = "alerts@mydomain.com"
today = str(datetime.datetime.now())
subject = "Database Alerts "
msg = MIMEMultipart("alternative")
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = subject + " " + today

#Log into mail server
server.login(fromaddr,my_pass)

#Config function
def server_config(filename, section):
    # create a parser
    parser = ConfigParser()
    # read config file
    try:
        parser.read(filename)
    except:
        slackupdates('localhost','locahost',0,'Section {0} not found in the {1} file'.format(section, filename))

    # get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        slackupdates('localhost','locahost',0,'Section {0} not found in the {1} file'.format(section, filename))
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

#Get server details
def get_servers():
    config = server_config('dbcreds.ini','localdb')
    conn = None
    try:
       # read connection parameters
       params = config

       # connect to the  server
       print('Connecting to local database... ' + str(datetime.datetime.now()))
       conn = psycopg2.connect(**params)
       cur = conn.cursor()
       # create a cursor
       print('Selecting all servers ' + str(datetime.datetime.now()))
       all_servers = cur.execute("select sname,endpoint from servers where active=true")
       result = cur.fetchall()
       for row in result:
           print(row['sname'], row['endpoint'])
           check_uptime(row['sname'],row['endpoint'])
       cur.close()
       print('Connection to local database closed ' + str(datetime.datetime.now()))

    except (Exception, psycopg2.DatabaseError) as error:
       print(error)
       print('Failed to connect to local database ' + str(datetime.datetime.now()))
       pass
    finally:
       if conn is not None:
           conn.close()


def slackupdates(serverip,endpoint,dakika,error=''):
    url = "https://slack_hook"
    notif = "Database " + serverip + " is offline for " + str(dakika) + " minutes"
    if(error==''):
        message = ("Endpoint {}".format(endpoint))
    else:
        message = ("Endpoint {}\n Error: {}".format(endpoint,error))
        notif = "Database " + serverip + " connection has been resolved"
    title = (f"{notif} :zap:")
    slack_data = {
        "username": "slack_updates",
        "icon_emoji": ":satellite:",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        # "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

def send_alert(serverip,endpoint,actioner):
     print("Sending email alert............ " +  str(datetime.datetime.now()))
     config = server_config('dbcreds.ini','localdb')
     conn = None
     try:
        # read connection parameters
        params = config
        print('Connecting to local database... ' + str(datetime.datetime.now()))
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("select confail from servers where sname='%s'" % serverip)
        sender = cur.fetchone()
        print(sender['confail'])
        if(actioner==1):
                print('Starting Insert of alert result in localdb ' + str(datetime.datetime.now()))
                cur.execute("INSERT INTO uptimealert(host,status,alertDate) VALUES(%s,%s,%s)", (str(serverip),"offline",str(datetime.datetime.now())))
                cur.execute("update servers set confail=confail+1 where sname='%s'" % serverip)
                conn.commit()
                if(sender['confail']==2 or (sender['confail']%4==0 and sender['confail']>0)):
                    dakika = sender['confail']*5
                    text = """Database """ + endpoint + """ is offline for """ + str(dakika) + """ minutes """
                    msg.attach(MIMEText(text, 'plain'))
                    server.sendmail(fromaddr, toaddr, msg.as_string())
                    print("Email sent at " +  str(datetime.datetime.now()))
                    print("\n\n")
                    slackupdates(serverip,endpoint,dakika)
                cur.close()
                print('Connection to local database closed ' + str(datetime.datetime.now()))
        else:
            if(sender['confail']==1):
                cur.execute("update servers set confail=0 where sname='%s'" % serverip)
                conn.commit()
                cur.close()
            elif(sender['confail']>1):
                cur.execute("update servers set confail=0 where sname='%s'" % serverip)
                conn.commit()
                cur.close()
                shida="Resolved!"
                dakika=0
                slackupdates(serverip,endpoint,dakika,shida)

     except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print('Failed to connect to local database ' + str(datetime.datetime.now()))
        pass
     finally:
        if conn is not None:
            conn.close()

def check_uptime(servername,endpoint):
    """ Connect to the database server """
    config = server_config('dbcreds.ini',servername)
    conn = None
    try:
        # read connection parameters
        params = config
        print('Connecting to ' + servername + ' database... ' + str(datetime.datetime.now()))
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if(conn):
            cur = conn.cursor()
            print('Connection to ' + servername + ' database successful at ' + str(datetime.datetime.now()))
            send_alert(servername,endpoint,0)
            dakika=0
        else:
            print('Connection to ' + servername + ' database failed at ' + str(datetime.datetime.now()))
            send_alert(servername,endpoint,1)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        send_alert(servername,endpoint,1)
        pass
    finally:
        if conn is not None:
            conn.close()
            print('Connection to ' + servername + ' database closed ' + str(datetime.datetime.now()))

if __name__ == '__main__':
    get_servers()
