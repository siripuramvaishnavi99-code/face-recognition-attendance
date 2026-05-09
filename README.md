# Face Recognition Attendance System

A GUI-based Face Recognition Attendance System developed using Python, OpenCV, Tkinter, and MySQL.  
The system captures student faces, trains a recognition model, detects faces in real time, and automatically marks attendance in a MySQL database.

---

# Features

- GUI Interface using Tkinter
- Face Registration and Training
- Real-Time Face Recognition
- Automatic Attendance Marking
- MySQL Database Integration
- Automatic Table Creation
- Camera-Based Attendance Verification
- Single File Python Project

---

# Technologies Used

- Python 3.10
- OpenCV
- OpenCV Contrib
- Tkinter
- NumPy
- Pillow
- MySQL
- XAMPP / PHPMyAdmin

---

# Project Structure

```text
FaceAttendance/
│
├── main.py
├── dataset/
└── trainer/
Installation
1. Install Python

Recommended Version:

Python 3.10

Download:
https://www.python.org/downloads/

2. Install Anaconda

Download:
https://www.anaconda.com/download

3. Install XAMPP

Download:
https://www.apachefriends.org/index.html

Start:

Apache
MySQL
Required Libraries

Run in Anaconda Prompt:

pip install opencv-python
pip install opencv-contrib-python
pip install numpy
pip install pillow
pip install mysql-connector-python
Database Setup

Open PHPMyAdmin:

http://localhost/phpmyadmin

Create database:

CREATE DATABASE face_attendance;

No need to create tables manually.
The program creates tables automatically.

How to Run

Open Anaconda Prompt.

Go to project folder:

cd Desktop
cd FaceAttendance

Run project:

python main.py
How It Works
Train New Face
Enter Student Name
Enter Roll Number
Click:
Train New Face

The system:

Opens camera
Captures 50 face samples
Trains face recognition model
Saves trained model automatically
Mark Attendance

Click:

Mark Attendance

The system:

Opens camera
Detects trained face
Recognizes user
Marks attendance automatically in MySQL database
Attendance Storage

Attendance records are stored in:

Database:

face_attendance

Table:

attendance
Exit Camera

Press:

ESC

to close camera window.

Future Improvements
Export Attendance to Excel
Admin Login System
Email Notifications
Flask Web Dashboard
Deep Learning Face Recognition
Multiple User Authentication
Author
247r1a05c2-b
