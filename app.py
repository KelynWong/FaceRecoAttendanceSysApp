import streamlit as st
import numpy as np
import pandas as pd
import time
import requests
import json
from datetime import datetime
from datetime import timedelta
import _strptime
from PIL import Image
import hashlib
import mysql.connector as mysql

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "password",
    database = "facerecognitionattendancesystem"
)

dbPassword = ''
name = ''
lecturerID = 0
datas = ''

studentName = []
present = []
dateTimeArrived = []
className = []
fromDateTime = []
toDateTime = []
status = []

dataFrame = []
dataFrameList = []

noOfDataFrames = 0

st.set_page_config(layout="wide")

statusBox = st.empty()
inputUsernameBox = st.empty()
inputPasswordBox = st.empty()
loginBtn = st.empty()
titleTxt = st.empty()

statusBox.warning("Please login first in order to view application!")

username = inputUsernameBox.text_input("Username")
password = inputPasswordBox.text_input("Password",type='password')
if loginBtn.button("Login"):
    hash_object = hashlib.md5(password.encode())
    hashed_pswd = hash_object.hexdigest()

    # fetch password from lecturer table in database
    cursor = db.cursor()
    query = 'SELECT Password, Name, LecturerID FROM Lecturer WHERE Username = "' + username + '"'
    cursor.execute(query)
    datas = cursor.fetchall()

    for data in datas:
        dbPassword = data[0]
        name = data[1]
        lecturerID = data[2]

    if hashed_pswd == dbPassword:
        statusBox.success("Logged In as {}".format(name))
        inputUsernameBox.empty()
        inputPasswordBox.empty()
        loginBtn.empty()

        # fetch lecturer
        cursor = db.cursor()
        query = "SELECT DISTINCT GROUP_CONCAT(student.Name) AS StudentName, GROUP_CONCAT(classattendance.Present) AS Present, GROUP_CONCAT(IFNULL(classattendance.DateTime, '-')) AS DateTimeArrived, class.Name AS ClassName, GROUP_CONCAT(DISTINCT FromDateTime) AS FromDateTime, GROUP_CONCAT(DISTINCT ToDateTime) AS ToDateTime FROM class INNER JOIN classattendance ON class.ClassID = classattendance.ClassID INNER JOIN student ON classattendance.StudentID = student.StudentID WHERE LecturerID = {} GROUP BY class.Name".format(str(lecturerID))
        cursor.execute(query)
        datas = cursor.fetchall()
        
        for data in datas:
            studentName.append(data[0].split(','))
            present.append(data[1].split(','))
            dateTimeArrived.append(data[2].split(','))
            className.append(data[3])
            fromDateTime.append(data[4])
            toDateTime.append(data[5])
            dataFrame.append(studentName)
            dataFrame.append(present)
            dataFrame.append(dateTimeArrived)
            dataFrame.append(className)
            dataFrame.append(fromDateTime)
            dataFrame.append(toDateTime)
            studentName = []
            present = []
            dateTimeArrived = []
            className = []
            fromDateTime = []
            toDateTime = []
            dataFrameList.append(dataFrame)
            dataFrame = []

        st.title('Face recognition system')
        st.header('Analytics')

        i = 0
        while i < len(dataFrameList):
            dataFrameInList = dataFrameList[i]
            j = 0
            while j < len(dataFrameInList[2][0]):
                if dataFrameInList[1][0][j] != '0' :
                    datePlus15Min = datetime.strptime(dataFrameInList[4][0], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=15)
                    if dataFrameInList[2][0][j] >= datePlus15Min.strftime("%Y-%m-%d %H:%M:%S"):
                        status.append("Late")
                    elif (dataFrameInList[2][0][j] >= dataFrameInList[4][0]) and (dataFrameInList[2][0][j] <= datePlus15Min.strftime("%Y-%m-%d %H:%M:%S")):
                        status.append("On Time")
                    else:
                        status.append("Early")
                else:
                    status.append("Absent")
                j = j + 1
            dataFrameInList.append(status)
            status = []
            st.subheader("Class: " + dataFrameInList[3][0])
            st.subheader("Start Time: " + dataFrameInList[4][0])
            st.subheader("End Time: " + dataFrameInList[5][0])
            col1, col2 = st.columns([2,3])
            df = pd.DataFrame({
                'studentName': dataFrameInList[0][0],
                'status': dataFrameInList[6],
                'dateTimeArrived': dataFrameInList[2][0],
            }, columns=['studentName','dateTimeArrived', 'status'])

            df = df.rename(columns={'studentName':'index'}).set_index('index')
            col1.subheader("Table of data")
            col1.write(df)
            col2.subheader("Chart of data")
            col2.line_chart(df)
            i = i + 1
    else:
        statusBox.error("Incorrect username or password. Please re-enter credentials and try again!")

