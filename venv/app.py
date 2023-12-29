from flask import Flask, render_template
import sqlite3

#configure application
app = Flask(__name__)


#connect to SQL db
def get_db():
    path = "C:\\Users\\owenr\\Documents\\GitHub\\cs50FinalProj\\venv\\assignments.db"
    return sqlite3.connect(path)


@app.route("/")
def index():

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT person_name FROM test WHERE person_id = ?", (1,)
    )
    name = cursor.fetchone()[0]
    conn.close()
    
    return render_template("index.html", name=name)


if __name__ == '__main__':
    app.run(debug=True)