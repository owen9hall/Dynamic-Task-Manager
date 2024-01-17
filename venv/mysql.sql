--DROP TABLE people;
CREATE TABLE IF NOT EXISTS people(person_id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL, password TEXT NOT NULL, date_type_setting TEXT NOT NULL DEFAULT "only dates");



--SELECT * FROM people;

-------------------------------------------

--DROP TABLE assignments;
CREATE TABLE IF NOT EXISTS assignments(assignment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
person_id INTEGER NOT NULL, assignment_name TEXT NOT NULL, class_name TEXT, due_date DATE, 
size INTEGER NOT NULL, description TEXT, archived BOOL NOT NULL, custom_order_val INTEGER NOT NULL); 


--SELECT * FROM assignments;

------------------------------------------
