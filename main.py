import cv2
import os
import numpy as np
from PIL import Image
import mysql.connector
import tkinter as tk
from tkinter import messagebox

# =====================================================
# DATABASE CONNECTION
# =====================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="face_attendance"
)

cursor = db.cursor()

# =====================================================
# CREATE TABLES
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    rollno VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    rollno VARCHAR(100),
    status VARCHAR(20),
    date DATE,
    time TIME
)
""")

db.commit()

# =====================================================
# CREATE FOLDERS
# =====================================================

if not os.path.exists("dataset"):
    os.makedirs("dataset")

if not os.path.exists("trainer"):
    os.makedirs("trainer")

# =====================================================
# FACE DETECTOR
# =====================================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

recognizer = cv2.face.LBPHFaceRecognizer_create()

# =====================================================
# TRAIN FACE FUNCTION
# =====================================================

def train_face():

    name = name_entry.get()
    rollno = roll_entry.get()

    if name == "" or rollno == "":

        messagebox.showerror(
            "Error",
            "Enter Name and Roll Number"
        )

        return

    sql = "INSERT INTO students(name, rollno) VALUES(%s,%s)"
    val = (name, rollno)

    cursor.execute(sql, val)

    db.commit()

    user_id = cursor.lastrowid

    path = f"dataset/User.{user_id}"

    if not os.path.exists(path):
        os.makedirs(path)

    cam = cv2.VideoCapture(0)

    if not cam.isOpened():

        messagebox.showerror(
            "Error",
            "Camera Not Opening"
        )

        return

    count = 0

    while True:

        ret, img = cam.read()

        if not ret:
            break

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            1.3,
            5
        )

        for (x, y, w, h) in faces:

            count += 1

            cv2.imwrite(
                f"{path}/{count}.jpg",
                gray[y:y+h, x:x+w]
            )

            cv2.rectangle(
                img,
                (x, y),
                (x+w, y+h),
                (255, 0, 0),
                2
            )

            cv2.putText(
                img,
                f"Samples: {count}/50",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Training Camera",
            img
        )

        key = cv2.waitKey(1) & 0xFF

        # ESC KEY
        if key == 27:
            break

        # WINDOW CLOSED
        if cv2.getWindowProperty(
            "Training Camera",
            cv2.WND_PROP_VISIBLE
        ) < 1:
            break

        if count >= 50:
            break

    cam.release()

    cv2.destroyAllWindows()

    # =====================================================
    # TRAIN MODEL
    # =====================================================

    faces = []
    ids = []

    for user_folder in os.listdir("dataset"):

        folder_path = os.path.join(
            "dataset",
            user_folder
        )

        for image in os.listdir(folder_path):

            img_path = os.path.join(
                folder_path,
                image
            )

            pil_img = Image.open(
                img_path
            ).convert('L')

            img_numpy = np.array(
                pil_img,
                'uint8'
            )

            id = int(
                user_folder.split(".")[1]
            )

            faces.append(img_numpy)

            ids.append(id)

    recognizer.train(
        faces,
        np.array(ids)
    )

    recognizer.save(
        "trainer/trainer.yml"
    )

    messagebox.showinfo(
        "Success",
        "Face Trained Successfully"
    )

# =====================================================
# MARK ATTENDANCE FUNCTION
# =====================================================

def mark_attendance():

    if not os.path.exists(
        "trainer/trainer.yml"
    ):

        messagebox.showerror(
            "Error",
            "No Trained Model Found"
        )

        return

    recognizer.read(
        "trainer/trainer.yml"
    )

    cam = cv2.VideoCapture(0)

    if not cam.isOpened():

        messagebox.showerror(
            "Error",
            "Camera Not Opening"
        )

        return

    marked_ids = []

    while True:

        ret, img = cam.read()

        if not ret:
            break

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            1.2,
            5
        )

        for (x, y, w, h) in faces:

            id, confidence = recognizer.predict(
                gray[y:y+h, x:x+w]
            )

            if confidence < 70:

                cursor.execute(
                    "SELECT name, rollno FROM students WHERE id=%s",
                    (id,)
                )

                result = cursor.fetchone()

                if result:

                    name = result[0]
                    rollno = result[1]

                    cv2.putText(
                        img,
                        name,
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                    if id not in marked_ids:

                        sql = """
                        INSERT INTO attendance
                        (name, rollno, status, date, time)
                        VALUES(%s,%s,%s,CURDATE(),CURTIME())
                        """

                        val = (
                            name,
                            rollno,
                            "Present"
                        )

                        cursor.execute(
                            sql,
                            val
                        )

                        db.commit()

                        marked_ids.append(id)

                        print(
                            name,
                            "Marked Present"
                        )

            else:

                cv2.putText(
                    img,
                    "Unknown",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            cv2.rectangle(
                img,
                (x, y),
                (x+w, y+h),
                (255, 0, 0),
                2
            )

        cv2.imshow(
            "Attendance Camera",
            img
        )

        key = cv2.waitKey(1) & 0xFF

        # ESC KEY
        if key == 27:
            break

        # WINDOW CLOSED
        if cv2.getWindowProperty(
            "Attendance Camera",
            cv2.WND_PROP_VISIBLE
        ) < 1:
            break

    cam.release()

    cv2.destroyAllWindows()

# =====================================================
# CLOSE APPLICATION
# =====================================================

def close_app():

    cv2.destroyAllWindows()

    root.destroy()

# =====================================================
# GUI
# =====================================================

root = tk.Tk()

root.title("Face Attendance System")

root.geometry("500x400")

root.configure(bg="white")

# TITLE

title = tk.Label(
    root,
    text="FACE ATTENDANCE SYSTEM",
    font=("Arial", 18, "bold"),
    bg="white",
    fg="blue"
)

title.pack(pady=20)

# NAME

name_label = tk.Label(
    root,
    text="Student Name",
    font=("Arial", 12),
    bg="white"
)

name_label.pack()

name_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

name_entry.pack(pady=10)

# ROLL NUMBER

roll_label = tk.Label(
    root,
    text="Roll Number",
    font=("Arial", 12),
    bg="white"
)

roll_label.pack()

roll_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

roll_entry.pack(pady=10)

# TRAIN BUTTON

train_btn = tk.Button(
    root,
    text="Train New Face",
    font=("Arial", 12, "bold"),
    bg="green",
    fg="white",
    width=20,
    command=train_face
)

train_btn.pack(pady=20)

# ATTENDANCE BUTTON

attendance_btn = tk.Button(
    root,
    text="Mark Attendance",
    font=("Arial", 12, "bold"),
    bg="blue",
    fg="white",
    width=20,
    command=mark_attendance
)

attendance_btn.pack(pady=10)

# EXIT BUTTON

exit_btn = tk.Button(
    root,
    text="Exit",
    font=("Arial", 12, "bold"),
    bg="red",
    fg="white",
    width=20,
    command=close_app
)

exit_btn.pack(pady=10)

root.mainloop()