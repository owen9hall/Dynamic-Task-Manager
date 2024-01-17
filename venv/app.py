from flask import Flask, render_template, session, request, redirect
import sqlite3
from datetime import date, datetime
from functools import wraps

app = Flask(__name__, static_url_path='', static_folder='static')

#configure application
app = Flask(__name__)
app.secret_key = '189jdxksf493k2kafag455'
todays_date = date.today().strftime("%Y-%m-%d") #YYYY-MM-DD

CUSTOM_ORDER_ARRAY = [ 
#   |1 |2 |3 | <- sizes
    [3, 2, 1],      # day 0
    [6, 5, 4],      # day 1
    [10, 8, 7],     # day 2
    [16, 11, 9],    # day 3
    [30, 12, 13],   # day 4
    [None, 17, 14],  # day 5
    [None, 20, 15],  # ...
    [None, 26, 18],
    [None, 29, 19],
    [None, None, 21],
    [None, None, 22],
    [None, None, 23],
    [None, None, 24],
    [None, None, 25],
    [None, None, 27],
    [None, None, 28], # day 15
]
CUSTOM_ORDER_ARRAY_VALS = 30 # 30 total items with non-None values in CUSTOM_ORDER_ARRAY
def not_in_custom_order_array(size):
    return CUSTOM_ORDER_ARRAY_VALS + 4 - size

def custom_order_value(flags, due_date_str):
    today = datetime.today()
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    day = (due_date - today).days + 1
    size = 1
    if flags == "🚩🚩🚩":
        size = 3
    elif flags == "🚩🚩":
        size = 2

    if due_date < today:
        return 0
    elif day > len(CUSTOM_ORDER_ARRAY) - 1 or CUSTOM_ORDER_ARRAY[day][size - 1] is None:
        return(not_in_custom_order_array(size))

    else:
        return CUSTOM_ORDER_ARRAY[day][size - 1]

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#connect to SQL db
def get_db():
    path = "C:\\Users\\owenr\\Documents\\GitHub\\cs50FinalProj\\venv\\assignments.db"
    return sqlite3.connect(path)

# HELPER METHOD
# makes due date a string in MM/DD/YYYY format
def convert_date_format(date_string):
    parts = date_string.split("-")  # Split the date string by "-"
    if len(parts) == 3:  # Ensure it's a valid date format
        return f"{parts[1]}/{parts[2]}/{parts[0]}"  # Rearrange parts in MM/DD/YYYY format
    else:
        return "Invalid date format"

def sort_by_assignment_name(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE person_id == ? ORDER BY LOWER(assignment_name) ASC, custom_order_val ASC, due_date ASC, LOWER(class_name) ASC", (userID,)
    )
    tableData = cursor.fetchall()
    conn.close()
    return tableData

def sort_by_class_name(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE person_id == ? ORDER BY LOWER(class_name) ASC, custom_order_val ASC, due_date ASC, LOWER(assignment_name) ASC", (userID,)
    )
    tableData = cursor.fetchall()
    conn.close()
    return tableData

def sort_by_due_date(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE person_id == ? ORDER BY due_date ASC, custom_order_val ASC, size DESC, LOWER(class_name) ASC, LOWER(assignment_name) ASC", (userID,)
    )
    tableData = cursor.fetchall()
    conn.close()
    return tableData

def sort_by_size(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE person_id == ? ORDER BY size DESC, custom_order_val ASC, due_date ASC, LOWER(class_name) ASC, LOWER(assignment_name) ASC", (userID,)
    )
    tableData = cursor.fetchall()
    conn.close()
    return tableData

def sort_by_custom_order(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE person_id == ? ORDER BY custom_order_val ASC, due_date ASC, LOWER(class_name) ASC, LOWER(assignment_name) ASC", (userID,)
    )
    tableData = cursor.fetchall()
    conn.close()
    return tableData

def load_table_data(tableData, htmlFilename, userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_type_setting FROM people WHERE person_id == ?", (userID,)
    )
    date_type = cursor.fetchone()[0]
    conn.close()


    assignment_ids = {}
    classes = []
    #tableData will have data in different order depending on the sort
    for rowData in tableData:
        # due_date becomes a word if certain num of days until due
        due_date_str = convert_date_format(rowData[4])
        due_date = datetime.strptime(rowData[4], "%Y-%m-%d")
        day_difference = (due_date - datetime.today()).days + 1

        if date_type != "only dates":
            if day_difference == 0:
                due_date_str = "Today"
            elif day_difference == 1:
                due_date_str = "Tomorrow"
            elif day_difference == -1:
                due_date_str = "Yesterday"
            
            if date_type == "only relative dates":
                if day_difference > 1:
                    due_date_str = f"In {day_difference} days"
                elif day_difference < -1:
                    due_date_str = f"{abs(day_difference)} days ago"

        assignment_id = rowData[0]
        assignment_ids[assignment_id] = {
            "person_id": rowData[1],
            "assignment_name": rowData[2],
            "class_name": rowData[3].capitalize(),
            "due_date": due_date_str,
            "size": rowData[5],
            "description": rowData[6],
            "archived": rowData[7]
        }

        if rowData[3] and not rowData[7] and rowData[3].capitalize() not in classes:
            classes.append(rowData[3].capitalize())
    
    return render_template(htmlFilename, assignment_ids=assignment_ids, todays_date=todays_date, classes=classes)

def update_custom_order_value(userID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT assignment_id, size, due_date FROM assignments WHERE person_id == ?",
        (userID,)
    )
    assignments_to_update = cursor.fetchall()

    for assignment in assignments_to_update:
        custom_order_val = custom_order_value(assignment[1], assignment[2])
        cursor.execute(
            "UPDATE assignments SET custom_order_val = ? WHERE assignment_id == ?",
            (custom_order_val, assignment[0])
        )

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    userID = session["user_id"]
    tableData = None

    update_custom_order_value(userID)

    if request.method == "POST":
        if "add_assignment_button" in request.form:
            assignment_name = request.form.get("assignment_name")
            class_name = request.form.get("class_name")
            due_date = request.form.get("due_date")
            size = request.form.get("size")
            description = request.form.get("description")
        
            custom_order_val = custom_order_value(size, due_date) # finds value for custom ordering

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assignments (person_id, assignment_name, class_name, due_date, size, description, archived, custom_order_val) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", 
                (userID, assignment_name, class_name.capitalize(), due_date, size, description, False, custom_order_val,)
            )
            conn.commit()
            conn.close()
            return redirect("/")

        elif "complete_assignment_button" in request.form:
            assignment_id = request.form["complete_assignment_button"]
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE assignments SET archived = ? WHERE assignment_id == ?", 
                (True, assignment_id,)
            )
            conn.commit()
            conn.close()
            return redirect("/")

        elif "sort_by_assignment_name" in request.form:
            tableData = sort_by_assignment_name(userID)
    
        elif "sort_by_class_name" in request.form:
            tableData = sort_by_class_name(userID)

        elif "sort_by_due_date" in request.form:
            tableData = sort_by_due_date(userID)
        
        elif "sort_by_size" in request.form:
            tableData = sort_by_size(userID)

    #default organization (custom order)
    if tableData is None:
        tableData = sort_by_custom_order(userID)

    return load_table_data(tableData, "index.html", userID)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("must provide password")

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT person_id FROM people WHERE username == ?", (username,)
        )
        username_person_id = cursor.fetchone()
        conn.close()
        if username_person_id is None:
            return error("invalid username or password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM people WHERE person_id == ?", (username_person_id[0],)
        )
        person_id_password = cursor.fetchone()
        conn.close()
        if person_id_password is None:
            return error("invalid username or password")
        
        if person_id_password[0] != password:
            return error("invalid username or password")
        
        session["user_id"] = username_person_id[0]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return error("must provide username")
        username = request.form.get("username")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM people WHERE username == ?", (username,)
        )
        matchingUsernames = cursor.fetchall()
        conn.close()
        if len(matchingUsernames) != 0:
            return error("username already exists")
        
        if not request.form.get("password"):
            return error("must provide password")
        password = request.form.get("password")
        if not request.form.get("confirmation"):
            return error ("must provide confirmation")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return error("password and confirmation must match")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO people (username, password) VALUES(?, ?)", (username, password,)
        )
        conn.commit()
        conn.close()
        
        return redirect("/")

    else:
        return render_template("register.html")

    

@app.route("/error")
def error(errorMsg):
    return render_template("error.html", errorMsg=errorMsg)

@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    if request.method == "POST":
        if request.form.get("unarchive"):
            unarchive_id = request.form.get("unarchive")
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE assignments SET archived = ? WHERE assignment_id == ?", (False, unarchive_id,)
            )
            conn.commit()
            conn.close()
        return redirect("/archive")

    else:
        userID = session["user_id"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignments WHERE person_id == ? AND archived == ?", (userID, True)
        )
        tableData = cursor.fetchall()
        conn.close()
        return load_table_data(tableData, "archive.html", userID)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    userID = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_type_setting FROM people WHERE person_id == ?",
        (userID,)
    )
    settings = cursor.fetchone()
    date_type_setting = settings[0]
    conn.close()

    if request.method == "POST":
        if request.form.get("date_types"):
            date_type_setting = request.form.get("date_types")
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE people SET date_type_setting = ? WHERE person_id == ?",
                (date_type_setting, userID,)
            )
            conn.commit()
            conn.close()

    return render_template("settings.html", date_type_setting=date_type_setting)

@app.route("/edit_assignment", methods=["GET", "POST"])
@login_required
def edit_assignment():
    userID = session["user_id"]
    tableData = None

    if request.method == "POST":
        if "sort_by_assignment_name" in request.form:
            tableData = sort_by_assignment_name(userID)
    
        elif "sort_by_class_name" in request.form:
            tableData = sort_by_class_name(userID)

        elif "sort_by_due_date" in request.form:
            tableData = sort_by_due_date(userID)
        
        elif "sort_by_size" in request.form:
            tableData = sort_by_size(userID)

        elif "edit_assignment_id" in request.form:
            assignment_id = request.form.get("edit_assignment_id")
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM assignments WHERE person_id == ? AND assignment_id == ?", (userID, assignment_id,)
            )
            assignment_id_to_edit = cursor.fetchone()
            conn.close()

            tableData = sort_by_custom_order(userID)

            assignment_ids = {}
            classes = []
            #tableData will have data in different order depending on the sort
            for rowData in tableData:
                assignment_id = rowData[0]
                assignment_ids[assignment_id] = {
                    "person_id": rowData[1],
                    "assignment_name": rowData[2],
                    "class_name": rowData[3].capitalize(),
                    "due_date": convert_date_format(rowData[4]),
                    "size": rowData[5],
                    "description": rowData[6],
                    "archived": rowData[7],
                    "due_date_unconverted": rowData[4]
                }
                if rowData[3] and not rowData[7] and rowData[3].capitalize() not in classes:
                    classes.append(rowData[3].capitalize())

            return render_template("edit_assignment.html", assignment_ids=assignment_ids, todays_date=todays_date, classes=classes, assignment_id_to_edit=assignment_id_to_edit[0])

        elif "save_edit" in request.form:
            assignment_id = request.form.get("assignment_id")
            assignment_name = request.form.get("assignment_name")
            class_name = request.form.get("class_name")
            due_date = request.form.get("due_date")
            size = request.form.get("size")
            description = request.form.get("description")
            custom_val = custom_order_value(size, due_date)

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE assignments SET assignment_name = ?, class_name = ?, due_date = ?, size = ?, description = ?, custom_order_val = ? WHERE assignment_id == ?", 
                (assignment_name, class_name, due_date, size, description, custom_val, assignment_id,) 
            )
            conn.commit()
            conn.close()
            return redirect("/")



    #default organization (custom order)
    if tableData is None:
        tableData = sort_by_custom_order(userID)

    return load_table_data(tableData, "edit_assignment.html", userID)


if __name__ == '__main__':
    app.run(debug=True)


