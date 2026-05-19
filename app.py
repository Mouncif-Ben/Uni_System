# Flask Framework 
from flask import Flask , render_template , jsonify, request

import sqlite3

# ── import your functions from model.py ──
from module1_prediction.model import (
    predict_all,
    get_stats,
    at_risk_by_filiere,
    at_risk_percentages,
    train_model
)

from module2_timetable.generator import(
  generate_cours_list,
  backtracking,
  salles_total,
  courses_total
)

import random


app = Flask(__name__)

DB = 'university.db'

def get_db():
  conn = sqlite3.connect(DB)
  conn.row_factory = sqlite3.Row # rows act like dicts
  return conn


@app.route("/")
@app.route("/dashboard")
def dashboard_page():
  students = predict_all()  
  status = get_stats()
  at_risk_par_filiere = at_risk_by_filiere()
  at_risk_percentage = at_risk_percentages()
  coursesTotal = courses_total()
  sallesTotal = salles_total()
  return render_template('dashboard.html',active='dashboard',students=students,status=status,at_risk_par_filiere=at_risk_par_filiere,at_risk_percentage=at_risk_percentage,coursesTotal=coursesTotal,sallesTotal=sallesTotal)
  
#-----Module1
@app.route("/students")
def students_page():
  conn = get_db()
  rows = conn.execute("SELECT * FROM students").fetchall()
  total = len(rows)
  at_risk = conn.execute("SELECT COUNT(*) FROM students WHERE at_risk=1").fetchone()[0]
  conn.close()
  return render_template(
    'students.html',
    active = 'students',
    students=rows,
    total=total,
    at_risk=at_risk
  )

@app.route("/predictions")
def predictions_page():
  predictions_result = predict_all()
  status = get_stats()
  return render_template('predictions.html',active="predictions",status=status,predictions_result=predictions_result)

@app.route("/timetable")
def timetable_page():
  return render_template('timetable.html',active='timetable')

@app.route("/classrooms")
def classrooms_page():
  return render_template('classrooms.html')

@app.route("/professors")
def professors_page():
  return render_template('professors.html')

# Voir button
@app.route('/student/<int:id>')
def student_detail(id):
  conn = get_db()
  # get this specific student by id
  student = conn.execute("SELECT * FROM students WHERE id=?",(id,)).fetchone()
  conn.close()
  #if student not found 
  if student is None:
    return "Student not found", 404
  # get prediction and score for this student
  import os
  MODEL_PATH = os.path.join('module1_prediction','model.pkl')
  score = None
  level = None
  prediction = None
  if os.path.exists(MODEL_PATH):
    import pickle
    import numpy as np
    #prepare features for this student only 
    X = np.array([[
      student['note'],
      student['assiduite'],
      student['participation'],
    ]])
    with open(MODEL_PATH,'rb') as f:
      model = pickle.load(f)
    prediction = int(model.predict(X)[0])
    score = int(model.predict_proba(X)[0][1]*100)

    if score >= 70:
      level = "A risque"
    elif score >= 40:
      level = 'Moyen'
    else:
      level = 'Safe'
  return render_template('student_detail.html',
                    active = 'students',
                    student = student,
                    score = score,
                    level = level,
                    prediction = prediction
  )


#-------Module2
@app.route("/generate")
def generate():
  filiere_id = request.args.get("filiere_id")

  conn = get_db()
  c = conn.cursor()
  
  salles = [
      dict(zip([col[0] for col in c.description], row))
      for row in c.execute("SELECT * FROM rooms")
  ]

  creneaux = [
      dict(zip([col[0] for col in c.description], row))
      for row in c.execute("SELECT * FROM slots")
  ]

  c.execute("SELECT * FROM professors")
  cols = [col[0] for col in c.description]
  profs_list = [dict(zip(cols, row)) for row in c.fetchall()]

  profs = {p["id"]: p["prenom"] + " " + p["nom"] for p in profs_list}

  conn.close()

  cours_list = generate_cours_list(filiere_id)
  solution = backtracking(cours_list, salles, creneaux)

  result = []
  if solution:
      for s in solution:
          nom_cours = s["cours"]["nom"]
          type_cours = None

          if nom_cours.endswith("CM"):
              nom_cours = nom_cours[:-2].strip()
              type_cours = "CM"
          elif nom_cours.endswith("TD"):
              nom_cours = nom_cours[:-2].strip()
              type_cours = "TD"
          elif nom_cours.endswith("TP"):
              nom_cours = nom_cours[:-2].strip()
              type_cours = "TP"

          result.append({
              "cours": nom_cours,
              "type": type_cours,
              "salle": s["salle"]["nom"],
              "creneau": s["creneau"]["temps"],
              "prof": profs.get(s["cours"]["prof_id"], "")
          })

  return jsonify(result)




@app.route("/api/profs", methods=["GET"])
def get_profs():
  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT * FROM professors")
  rows = c.fetchall()
  cols = [col[0] for col in c.description]
  data = [dict(zip(cols, row)) for row in rows]
  conn.close()
  return jsonify(data)


@app.route("/api/profs", methods=["POST"])
def add_prof():
  data = request.json
  conn = get_db()
  c = conn.cursor()
  c.execute("""
      INSERT INTO professors (nom, prenom, email, specialite)
      VALUES (?, ?, ?, ?)
  """, (data["nom"], data["prenom"], data["email"], data["specialite"]))
  conn.commit()
  conn.close()
  return jsonify({"status": "ok"})


@app.route("/api/profs/<int:id>", methods=["PUT"])
def update_prof(id):
  data = request.json
  conn = get_db()
  c = conn.cursor()
  c.execute("""
      UPDATE professors SET nom=?, prenom=?, email=?, specialite=? WHERE id=?
  """, (data["nom"], data["prenom"], data["email"], data["specialite"], id))
  conn.commit()
  conn.close()
  return jsonify({"status": "ok"})


@app.route("/api/profs/<int:id>", methods=["DELETE"])
def delete_prof(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM professors WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/api/salles", methods=["GET"])
def get_salles():
  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT * FROM rooms")
  cols = [col[0] for col in c.description]
  data = [dict(zip(cols, row)) for row in c.fetchall()]
  conn.close()
  return jsonify(data)


@app.route("/api/salles", methods=["POST"])
def add_salle():
  data = request.json
  conn = get_db()
  c = conn.cursor()
  c.execute("""
      INSERT INTO rooms (nom, capacite, labo)
      VALUES (?, ?, ?)
  """, (data["nom"], data["capacite"], data.get("labo", 0)))
  conn.commit()
  conn.close()
  return jsonify({"status": "ok"})


@app.route("/api/salles/<int:id>", methods=["PUT"])
def update_salle(id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE rooms SET nom=?, capacite=?, labo=? WHERE id=?
    """, (data["nom"], data["capacite"], data.get("labo", 0), id))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/salles/<int:id>", methods=["DELETE"])
def delete_salle(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM rooms WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/api/filieres", methods=["GET"])
def get_filieres():
  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT * FROM filiere")
  cols = [col[0] for col in c.description]
  filieres = [dict(zip(cols, row)) for row in c.fetchall()]

  result = []
  for f in filieres:
    c.execute("SELECT * FROM groupe WHERE filiere_id = ?", (f["id"],))
    gcols = [col[0] for col in c.description]
    groupes = [dict(zip(gcols, row)) for row in c.fetchall()]

    nb_td = len([g for g in groupes if "TD" in g["nom"]])
    nb_tp = len([g for g in groupes if "TP" in g["nom"]])

    c.execute("""
        SELECT COALESCE(MAX(nb_etudiants), 0)
        FROM course
        JOIN groupe ON cours.groupe_id = groupe.id
        WHERE groupe.filiere_id = ? AND cours.nom LIKE '%CM%'
    """, (f["id"],))
    row = c.fetchone()
    nb_etudiants = row[0] if row else 0

    result.append({
        "id": f["id"],
        "nom": f["nom"],
        "nb_etudiants": nb_etudiants,
        "nb_td": nb_td,
        "nb_tp": nb_tp,
        "groupes": groupes
    })

    conn.close()
    return jsonify(result)


@app.route("/api/filieres", methods=["POST"])
def add_filiere():
  data = request.json
  conn = get_db()
  c = conn.cursor()

  c.execute("INSERT INTO filiere (nom) VALUES (?)", (data["nom"],))
  filiere_id = c.lastrowid

  nb_td = int(data.get("nb_td", 1))
  nb_tp = int(data.get("nb_tp", 1))

  for i in range(1, nb_td + 1):
      c.execute("INSERT INTO groupe (nom, filiere_id) VALUES (?, ?)",
                (f"TD{i}_F{filiere_id}", filiere_id))

  for i in range(1, nb_tp + 1):
      c.execute("INSERT INTO groupe (nom, filiere_id) VALUES (?, ?)",
                (f"TP{i}_F{filiere_id}", filiere_id))

  conn.commit()
  conn.close()
  return jsonify({"status": "ok", "id": filiere_id})


@app.route("/api/filieres/<int:id>", methods=["PUT"])
def update_filiere(id):
  data = request.json
  conn = get_db()
  c = conn.cursor()

  c.execute("UPDATE filiere SET nom=? WHERE id=?", (data["nom"], id))

  
  c.execute("DELETE FROM groupe WHERE filiere_id=?", (id,))

  nb_td = int(data.get("nb_td", 1))
  nb_tp = int(data.get("nb_tp", 1))

  for i in range(1, nb_td + 1):
      c.execute("INSERT INTO groupe (nom, filiere_id) VALUES (?, ?)",
                (f"TD{i}_F{id}", id))

  for i in range(1, nb_tp + 1):
      c.execute("INSERT INTO groupe (nom, filiere_id) VALUES (?, ?)",
                (f"TP{i}_F{id}", id))

  conn.commit()
  conn.close()
  return jsonify({"status": "ok"})


@app.route("/api/filieres/<int:id>", methods=["DELETE"])
def delete_filiere(id):
  conn = get_db()
  c = conn.cursor()
  c.execute("DELETE FROM groupe WHERE filiere_id=?", (id,))
  c.execute("DELETE FROM filiere WHERE id=?", (id,))
  conn.commit()
  conn.close()
  return jsonify({"status": "deleted"})

@app.route("/api/filieres/list", methods=["GET"])
def list_filieres():
  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT * FROM filiere")
  cols = [col[0] for col in c.description]
  data = [dict(zip(cols, row)) for row in c.fetchall()]
  conn.close()
  return jsonify(data)



#------Database
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

  cur.execute("""CREATE TABLE IF NOT EXISTS filiere (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT
    )
  """)

  cur.execute("""CREATE TABLE IF NOT EXISTS professors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nom TEXT,
      prenom TEXT,
      email TEXT,
      specialite TEXT
    )
  """)  

  cur.execute("""CREATE TABLE IF NOT EXISTS rooms(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nom TEXT NOT NULL,
      capacite INTEGER,
      labo INTEGER DEFAULT 0
    )
  """)

  cur.execute("""CREATE TABLE IF NOT EXISTS groupe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        filiere_id INTEGER
    )
    """)
    
  cur.execute("""CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temps TEXT
    )
    """)

  cur.execute("""CREATE TABLE IF NOT EXISTS course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prof_id INTEGER,
        groupe_id INTEGER,
        nb_etudiants INTEGER,
        besoin_labo INTEGER
    )
  """)

  conn.commit()
  conn.close()

def get_random_prof(conn):
  c = get_db()
  c = conn.cursor()
  c.execute("SELECT id FROM professors")
  profs = [row[0] for row in c.fetchall()]
  return random.choice(profs) if profs else None


FILIERES = {
    "S1": {
        "S1 Tronc Commun MI": ["Analyse 1", "Algebre 1", "Info 1", "Physique 1", "Anglais"],
        "S1 Tronc Commun PC": ["Analyse 1", "Algebre 1", "Chimie 1", "Physique 1", "Anglais"],
    },
    "S2": {
        "S2 Tronc Commun MI": ["Analyse 2", "Algebre 2", "Info 2", "Physique 2", "Francais"],
        "S2 Tronc Commun PC": ["Analyse 2", "Algebre 2", "Chimie 2", "Physique 2", "Francais"],
    },
    "S3": {
        "S3 MI": ["Analyse 3", "Algebre 3", "Programmation", "Electronique", "Proba"],
        "S3 PC": ["Thermodynamique", "Optique", "Chimie Organique", "Algebre 3", "Proba"],
    },
    "S4": {
        "S4 MI": ["Analyse 4", "Systemes", "Reseaux", "POO", "Statistiques"],
        "S4 PC": ["Mecanique", "Electromagnetisme", "Chimie Analytique", "Statistiques", "POO"],
    },
    "S5": {
        "S5 MI": ["IA", "BD", "Compilation", "Systemes Distribues", "Securite"],
        "S5 Math": ["Topologie", "Analyse Fonctionnelle", "Algebre 5", "Probabilites", "Geometrie"],
    },
    "S6": {
        "S6 2IDL": ["Genie Logiciel", "Architecture", "DevOps", "Machine Learning", "PFE"],
        "S6 P_IME": ["Mathematiques Appliquees", "Modelisation", "Simulation", "Optimisation", "PFE"],
    },
}

def insert_to_tables():
  conn = sqlite3.connect('university.db')
  c = conn.cursor()

  tables = ["students","filiere", "professors", "rooms", "course", "slots", "groupe"]

  for t in tables:
    c.execute(f"DELETE FROM {t}")

  # ---------------- STUDENTS ----------------
  students = [
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

  c.executemany("""
  INSERT INTO students (nom, note, assiduite, participation, at_risk, filiere)
  VALUES (?, ?, ?, ?, ?, ?)
  """, students)

  # ---------------- PROFESSORS ----------------
  profs = [
      ("Yassine", "Dr", "yassine@univ.ma", "Algo"),
      ("Ahmed",   "Dr", "ahmed@univ.ma",   "BD"),
      ("Ali",     "Dr", "ali@univ.ma",     "Reseaux"),
      ("Sara",    "Dr", "sara@univ.ma",    "Python"),
      ("Fatima",  "Dr", "fatima@univ.ma",  "IA"),
      ("Hassan",  "Dr", "hassan@univ.ma",  "Systeme"),
      ("Salma",   "Dr", "salma@univ.ma",   "Web"),
      ("Karim",   "Dr", "karim@univ.ma",   "Algo"),
      ("Noura",   "Dr", "noura@univ.ma",   "BD"),
      ("Imane",   "Dr", "imane@univ.ma",   "IA"),
      ("Rachid",  "Dr", "rachid@univ.ma",  "Maths"),
      ("Zineb",   "Dr", "zineb@univ.ma",   "Physique"),
      ("Omar",    "Dr", "omar@univ.ma",    "Chimie"),
      ("Laila",   "Dr", "laila@univ.ma",   "Analyse"),
      ("Younes",  "Dr", "younes@univ.ma",  "Algebre"),
  ]
  
  c.executemany("""
      INSERT INTO professors (nom, prenom, email, specialite)
      VALUES (?, ?, ?, ?)
  """, profs)

  # ---------------- ROOMS ----------------
  salles = []
  for i in range(1, 9):
      salles.append((i, f"Amphi {i}", 200, 0))
  sid = 9
  for i in range(1, 41):
      labo = 1 if i % 3 == 0 else 0
      salles.append((sid, str(i), 30 + (i % 10), labo))
      sid += 1
  c.executemany("INSERT INTO rooms VALUES (?,?,?,?)", salles)

  
  # ---------------- SLOTS ----------------
  jours  = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
  heures = ["08:30", "10:15", "12:00", "14:30", "16:15"]
  creneaux = []
  cid = 1
  for j in jours:
      for h in heures:
          if j == "Samedi" and h in ["14:30", "16:15"]:
              continue
          creneaux.append((cid, f"{j} {h}"))
          cid += 1
  c.executemany("INSERT INTO slots VALUES (?, ?)", creneaux)

  # ---------------- FILIERES ----------------
  filiere_id = 1
  groupe_id  = 1
  cours_id   = 1

  for semestre, filieres in FILIERES.items():
      for filiere_nom, modules in filieres.items():

          
          c.execute("INSERT INTO filiere (id, nom) VALUES (?, ?)",
                    (filiere_id, filiere_nom))

          
          groupes_ids = []
          for gi in range(1, 3):
              c.execute("INSERT INTO groupe (id, nom, filiere_id) VALUES (?, ?, ?)",
                        (groupe_id, f"TD{gi}_{filiere_nom}", filiere_id))
              groupes_ids.append(groupe_id)
              groupe_id += 1

          
          tp_groupes_ids = []
          for gi in range(1, 3):
              c.execute("INSERT INTO groupe (id, nom, filiere_id) VALUES (?, ?, ?)",
                        (groupe_id, f"TP{gi}_{filiere_nom}", filiere_id))
              tp_groupes_ids.append(groupe_id)
              groupe_id += 1

          
          for module in modules:
              prof_id = get_random_prof(conn)

              
              c.execute("""
                  INSERT INTO course (id, nom, prof_id, groupe_id, nb_etudiants, besoin_labo)
                  VALUES (?, ?, ?, ?, ?, ?)
              """, (cours_id, f"{module} CM", prof_id, groupes_ids[0], 150, 0))
              cours_id += 1

              
              for gid in groupes_ids:
                  c.execute("""
                      INSERT INTO course (id, nom, prof_id, groupe_id, nb_etudiants, besoin_labo)
                      VALUES (?, ?, ?, ?, ?, ?)
                  """, (cours_id, f"{module} TD", prof_id, gid, 35, 0))
                  cours_id += 1

              
              for gid in tp_groupes_ids:
                  c.execute("""
                      INSERT INTO course (id, nom, prof_id, groupe_id, nb_etudiants, besoin_labo)
                      VALUES (?, ?, ?, ?, ?, ?)
                  """, (cours_id, f"{module} TP", prof_id, gid, 25, 1))
                  cours_id += 1

          filiere_id += 1

  conn.commit()
  conn.close()

  print("DATABASE READY ")
  print("\nFilières créées:")
  for sem, filieres in FILIERES.items():
      for nom in filieres:
        print(f"  {nom}")



# __name__ controls what code actually executes
if __name__ == "__main__":
  app.run(debug=True)


