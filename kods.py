from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)
DATUBAZE = 'gramatu_klubs.db'

GRAMATAS = ["1984", "Lielais Getsbijs", "Svešā seja", "Kliedziens klusumā"]


def iegut_datubazi():
    if 'db' not in g:
        g.db = sqlite3.connect(DATUBAZE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def aizvert_datubazi(klauda):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def inicializet_datubazi():
    db = iegut_datubazi()
    db.execute('CREATE TABLE IF NOT EXISTS gramatas (id INTEGER PRIMARY KEY AUTOINCREMENT, nosaukums TEXT UNIQUE)')
    db.execute('''
        CREATE TABLE IF NOT EXISTS dalibnieki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vards TEXT NOT NULL,
            gramata_id INTEGER,
            FOREIGN KEY(gramata_id) REFERENCES gramatas(id)
        )
    ''')
    db.commit()


@app.route("/")
def sakums():
    return render_template("sakums.html", gramatas=GRAMATAS)

@app.route("/registre", methods=["POST"])
def registre():
    vards = request.form.get("vards")
    gramatas_nosaukums = request.form.get("gramata")

    if not vards:
        return render_template("kluda.html", zina="Nav ievadīts vārds!")
    if not gramatas_nosaukums:
        return render_template("kluda.html", zina="Nav izvēlēta grāmata!")

    db = iegut_datubazi()
    db.execute("INSERT OR IGNORE INTO gramatas (nosaukums) VALUES (?)", (gramatas_nosaukums,))
    db.commit()

    gramata_id = db.execute("SELECT id FROM gramatas WHERE nosaukums = ?", (gramatas_nosaukums,)).fetchone()["id"]

    db.execute("INSERT INTO dalibnieki (vards, gramata_id) VALUES (?, ?)", (vards, gramata_id))
    db.commit()

    return render_template("veiksmigi.html")

@app.route("/dalibnieki")
def paradit_dalibniekus():
    db = iegut_datubazi()
    rezultati = db.execute('''
        SELECT dalibnieki.vards, gramatas.nosaukums
        FROM dalibnieki
        JOIN gramatas ON dalibnieki.gramata_id = gramatas.id
    ''').fetchall()
    return render_template("dalibnieki.html", dalibnieki=rezultati)


if __name__ == "__main__":
    with app.app_context():
        inicializet_datubazi()
    app.run(debug=True)
