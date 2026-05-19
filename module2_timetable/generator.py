import sqlite3
import random
import time
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR,'university.db')

def get_db():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row # rows act like dicts
  return conn

def salles_total():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM rooms",conn)
    conn.close()
    return len(df)

def courses_total():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM course",conn)
    conn.close()
    return len(df)




def generate_cours_list(filiere_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT course.*
        FROM course
        JOIN groupe ON course.groupe_id = groupe.id
        WHERE groupe.filiere_id = ?
    """, (filiere_id,))

    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    all_cours = [dict(zip(columns, row)) for row in rows]

    conn.close()

    groupes = list(set([c["groupe_id"] for c in all_cours]))

    if not groupes:
        return []

    gid = groupes[0]

    cm = [c for c in all_cours if c["groupe_id"] == gid and "CM" in c["nom"]][:7]
    td = [c for c in all_cours if c["groupe_id"] == gid and "TD" in c["nom"]][:5]
    tp = [c for c in all_cours if c["groupe_id"] == gid and "TP" in c["nom"]][:2]

    return cm + td + tp



def is_valid(solution, cours, salle, creneau):

    for s in solution:
      if s["salle"]["id"] == salle["id"] and s["creneau"]["id"] == creneau["id"]:
          return False

       
      if s["cours"].get("prof_id") == cours.get("prof_id") and s["creneau"]["id"] == creneau["id"]:
          return False

       
      if s["cours"]["groupe_id"] == cours["groupe_id"] and s["creneau"]["id"] == creneau["id"]:
          return False

   
    if cours.get("nb_etudiants", 0) > salle["capacite"]:
        return False

    
    if cours.get("besoin_labo", 0) == 1 and salle["labo"] == 0:
        return False

    return True



def backtracking(cours_list, salles, creneaux, solution=None, index=0, start_time=None):

    if solution is None:
        solution = []

    if start_time is None:
        start_time = time.time()

    
    if time.time() - start_time > 10:
        return None

    if index >= len(cours_list):
        return solution

    cours = cours_list[index]

 
    if cours.get("prof_id") is None:
      conn = get_db()
      c = conn.cursor()
      c.execute("SELECT id FROM professors")
      profs = [p[0] for p in c.fetchall()]
      conn.close()
      if profs:
          cours["prof_id"] = random.choice(profs)

    
    if "CM" in cours["nom"]:
        salles_possibles = [s for s in salles if s["capacite"] >= 150]
    else:
        salles_possibles = [s for s in salles if s["capacite"] < 150]

    random.shuffle(salles_possibles)
    random.shuffle(creneaux)

    for creneau in creneaux:
        for salle in salles_possibles:
            if is_valid(solution, cours, salle, creneau):

                solution.append({
                    "cours": cours,
                    "salle": salle,
                    "creneau": creneau
                })

                result = backtracking(cours_list, salles, creneaux, solution, index + 1, start_time)

                if result is not None:
                    return result

                solution.pop()

    return None