# Monitor multiple PostgreSQL databases
Monitor PostgreSQL using python, with email and slack alerts!

INSTALLATION
1. Install python and the following packages:
 - psycopg2
 - smtplib
 - email
 - time
 - csv
 - configparser
 - requests
 - json

dnf install python
python3 -m pip install json

2. Install PostgreSQL
dnf install postgresql15-server

3. Create a database for the application.
create database monitordb;

4. Create the tables in the file db.sql

5. Insert database hosts to be monitored.
insert into servers values (null,'dbserver1','ip_address',1,0);

6. Create a slack incoming hook at slack.com

7. Edit the python file with the following details:
 - Email username and password, from address, to address, slack hook.

8. Edit the file dbcreds.ini with database host details. Sample has been given.

9. Execute the file and test, then add it to cron with your desired frequency.
python monitordbs.py
