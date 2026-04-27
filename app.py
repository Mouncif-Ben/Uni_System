# Flask Framework 
from flask import Flask , render_template , jsonify

import sqlite3

# Pandas
import pandas as pd

# Numpy
import numpy as np

# Scikit-learn (ML)
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# ── import your functions from model.py ──
from module1_prediction.model import (
    predict_all,
    get_stats,
    at_risk_by_filiere,
    at_risk_percentages,
    train_model
)

app = Flask(__name__)

DB = 'university.db'

def get_db():
  conn = sqlite3.connect(DB)
  conn.row_factory = sqlite3.Row # rows act like dicts
  return conn

@app.route("/")

def dashboard_page():
  students = predict_all()  
  status = get_stats()
  at_risk_par_filiere = at_risk_by_filiere()
  at_risk_percentage = at_risk_percentages()
  return render_template('dashboard.html',students=students,status=status,at_risk_par_filiere=at_risk_par_filiere,at_risk_percentage=at_risk_percentage)
  
@app.route("/students")

def students_page():
  conn = get_db()
  rows = conn.execute("SELECT * FROM students").fetchall()
  total = len(rows)
  at_risk = conn.execute("SELECT COUNT(*) FROM students WHERE at_risk=1").fetchone()[0]
  conn.close()
  return render_template(
    'students.html',
    students=rows,
    total=total,
    at_risk=at_risk
  )

@app.route("/timetable")

def timetable_page():
  return render_template('timetable.html')

def create_tables():
  conn = sqlite3.connect("university.db")
  cur = conn.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS students(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nom TEXT NOT NULL,
              filiere TEXT,
              note REAL,
              assiduite REAL,
              participation REAL,
              at_risk INTEGER DEFAULT 0
              )
              """)

  cur.execute("""CREATE TABLE IF NOT EXISTS rooms(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nom TEXT NOT NULL,
      capacite INTEGER,
      est_labo INTEGER DEFAULT 0
    )
  """)

  cur.execute("""CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        matiere TEXT
    )
  """)

  cur.execute("""CREATE TABLE IF NOT EXISTS slots(
        id INTEGER PRIMARY KEY,
        jour TEXT,
        heure_debut TEXT,
        heur_fin TEXT
    )
  """)

  cur.execute("""CREATE TABLE IF NOT EXISTS timetable(
          id INTEGER PRIMARY KEY,
          matiere TEXT,
          prof_id INTEGER,
          room_id INTEGER,
          solt_id INTEGER
    )
  """)

  conn.commit()
  conn.close()

def insert_to_tables():
  conn = sqlite3.connect('university.db')
  cursor = conn.cursor()

  # ---------------- STUDENTS ----------------
  students_data = [
    ("Ali", 12.5, 80, 70, 0, "Informatique"),
    ("Sara", 15.0, 90, 85, 0, "Mathématiques"),
    ("Omar", 8.0, 50, 40, 1, "Physique"),
    ("Lina", 17.5, 95, 90, 0, "Chimie"),
    ("Youssef", 9.5, 60, 50, 1, "Biologie"),
    ("Nora", 13.0, 85, 75, 0, "Géologie"),
    ("Karim", 7.0, 40, 30, 1, "Informatique"),
    ("Salma", 16.0, 92, 88, 0, "Mathématiques"),
    ("Hassan", 10.5, 70, 65, 0, "Physique"),
    ("Meriem", 14.5, 88, 80, 0, "Chimie"),
    ("Anas", 6.5, 35, 25, 1, "Biologie"),
    ("Fatima", 18.0, 98, 95, 0, "Géologie"),
    ("Rachid", 11.0, 75, 60, 0, "Mathématiques"),
    ("Imane", 13.5, 82, 78, 0, "Physique"),
    ("Hamza", 5.5, 30, 20, 1, "Chimie"),
    ("Zakaria", 14.0, 87, 80, 0, "Informatique"),
    ("Hind", 16.5, 93, 90, 0, "Mathématiques"),
    ("Mehdi", 9.0, 55, 45, 1, "Physique"),
    ("Aya", 17.0, 96, 92, 0, "Chimie"),
    ("Taha", 10.0, 65, 60, 0, "Biologie"),

    ("Khadija", 12.0, 78, 70, 0, "Géologie"),
    ("Reda", 6.0, 25, 20, 1, "Informatique"),
    ("Imad", 15.5, 91, 88, 0, "Mathématiques"),
    ("Sofia", 13.0, 83, 77, 0, "Physique"),
    ("Bilal", 8.5, 48, 42, 1, "Chimie"),

    ("Zineb", 16.8, 94, 90, 0, "Biologie"),
    ("Ayoub", 11.5, 76, 68, 0, "Géologie"),
    ("Mouad", 7.5, 38, 30, 1, "Informatique"),
    ("Laila", 14.2, 86, 82, 0, "Mathématiques"),
    ("Yasmin", 18.5, 99, 97, 0, "Physique"),

    ("Said", 9.8, 62, 55, 0, "Chimie"),
    ("Wafae", 15.8, 89, 84, 0, "Biologie"),
    ("Oussama", 5.0, 20, 15, 1, "Géologie"),
    ("Nada", 17.2, 95, 93, 0, "Informatique"),
    ("Anass", 10.8, 72, 66, 0, "Mathématiques"),

    ("Ilham", 13.8, 84, 79, 0, "Physique"),
    ("Samir", 6.8, 33, 28, 1, "Chimie"),
    ("Hajar", 16.2, 91, 87, 0, "Biologie"),
    ("Fouad", 12.8, 80, 73, 0, "Géologie"),
    ("Maya", 14.8, 88, 85, 0, "Informatique")
  ]
  
  cursor.executemany("""
  INSERT INTO students (nom, note, assiduite, participation, at_risk, filiere)
  VALUES (?, ?, ?, ?, ?, ?)
  """, students_data)
  
  

# # ---------------- ROOMS ----------------
# rooms_data = [
# ("Salle 101", 30, 0),
# ("Salle 102", 40, 0),
# ("Salle 103", 35, 0),
# ("Salle 104", 50, 0),
# ("Labo Info 1", 25, 1),
# ("Labo Info 2", 20, 1),
# ("Labo Physique", 15, 1),
# ("Salle 105", 45, 0)
# ]

# cursor.executemany("""
# INSERT INTO rooms (nom, capacite, est_labo)
# VALUES (?, ?, ?)
# """, rooms_data)

# # ---------------- PROFESSORS ----------------
# professors_data = [
# ("Ahmed", "Math"),
# ("Sara", "Physics"),
# ("Karim", "Computer Science"),
# ("Nora", "English"),
# ("Ali", "Chemistry"),
# ("Fatima", "Biology"),
# ("Hassan", "Statistics"),
# ("Salma", "AI")
# ]

# cursor.executemany("""
# INSERT INTO professors (nom, matiere)
# VALUES (?, ?)
# """, professors_data)

# # ---------------- SLOTS ----------------
# slots_data = [
# ("Monday", "08:00", "10:00"),
# ("Monday", "10:00", "12:00"),
# ("Tuesday", "08:00", "10:00"),
# ("Tuesday", "10:00", "12:00"),
# ("Wednesday", "08:00", "10:00"),
# ("Wednesday", "10:00", "12:00"),
# ("Thursday", "08:00", "10:00"),
# ("Friday", "10:00", "12:00")
# ]

# cursor.executemany("""
# INSERT INTO slots (jour, heure_debut, heure_fin)
# VALUES (?, ?, ?)
# """, slots_data)

# # ---------------- TIMETABLE ----------------
# timetable_data = [
# ("Math", 1, 1, 1),
# ("Physics", 2, 5, 2),
# ("Computer Science", 3, 6, 3),
# ("English", 4, 2, 4),
# ("Chemistry", 5, 7, 5),
# ("Biology", 6, 3, 6),
# ("Statistics", 7, 4, 7),
# ("AI", 8, 6, 8)
# ]

# cursor.executemany("""
# INSERT INTO timetable (matiere, prof_id, room_id, slot_id)
# VALUES (?, ?, ?, ?)
# """, timetable_data)



  conn.commit()
  

  conn.close()


# __name__ controls what code actually executes
if __name__ == "__main__":
  app.run(debug=True)


