from flask import Flask, request, render_template
from flaskext.mysql import MySQL
import os

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'xxxxx'
app.config['MYSQL_DATABASE_DB'] = 'phonebook'
app.config['MYSQL_DATABASE_PORT'] = 3306

mysql = MySQL()
mysql.init_app(app) 
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

def init_phonebook_db():
    phonebook_table = """
    CREATE TABLE IF NOT EXISTS phonebook.phonebook(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(phonebook_table)

def find_persons(keyword):
    query = f"""
    SELECT * FROM phonebook WHERE name like '%{keyword.strip().lower()}%';
    """
    cursor.execute(query)
    result = cursor.fetchall() 
    persons =[{'id':row[0], 'name':row[1].strip().title(), 'number':row[2]} for row in result]
    if len(persons) == 0:
        persons = [{'name':'No Result', 'number':'No Result'}] 
    return persons

def insert_person(name, number):
    query = f"""
    SELECT * FROM phonebook WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None: 
        return f'Person with name {row[1].title()} already exits.'

    insert = f"""
    INSERT INTO phonebook (name, number)
    VALUES ('{name.strip().lower()}', '{number}');
    """
    cursor.execute(insert)
    result = cursor.fetchall()
    return f'Person {name.strip().title()} added to Phonebook successfully'

def update_person(name, number):
    query = f"""
    SELECT * FROM phonebook WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None: 
        return f'Person with name {name.strip().title()} does not exist.'
    update = f"""
    UPDATE phonebook
    SET name='{row[1]}', number = '{number}'
    WHERE id= {row[0]};
    """
    cursor.execute(update)

    return f'Phone record of {name.strip().title()} is updated successfully'


# Write a function named `delete_person` which deletes person record from the phonebook table in the db,
# and returns returns text info about result of the operation
def delete_person(name):
    query = f"""
    SELECT * FROM phonebook WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None: # Again we need to control if we have this person. then, If we don't have, there is seen a warning massage like this
        return f'Person with name {name.strip().title()} does not exist, no need to delete.'

    # If we have this person, we'll delete his row using the querry.
    delete = f"""
    DELETE FROM phonebook
    WHERE id= {row[0]};
    """
    cursor.execute(delete) # And a magssage will be shown to be informed.
    return f'Phone record of {name.strip().title()} is deleted from the phonebook successfully'

# Write a function named `find_records` which finds phone records by keyword using `GET` and `POST` methods,
# using template files named `index.html` given under `templates` folder
# and assign to the static route of ('/')
@app.route('/', methods=['GET', 'POST'])
def find_records():
    if request.method == 'POST':
        keyword = request.form['username']
        persons_app = find_persons(keyword) # to avoid confusion, I use person_app in this application, and use person_html for html file.
        return render_template('index.html', persons_html=persons_app, keyword=keyword, show_result=True, developer_name='Turan')
    else:
        return render_template('index.html', show_result=False, developer_name='Turan')


# Write a function named `add_record` which inserts new record to the database using `GET` and `POST` methods,
# using template files named `add-update.html` given under `templates` folder
# and assign to the static route of ('add')
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        name = request.form['username'] # I'll get input from html file and assign it to name variable
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='save', developer_name='Turan')
        elif name.isdecimal(): # This will check if the name given by user has any decimal character. If it has, a warning massage will raise 
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name of person should be text', show_result=False, action_name='save', developer_name='Turan')
        # We'll check the phone number given by user here 
        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "": # The user may have forgotten to give a number. This function will control whether the phone number is empty or not. if it is empty, a warning massage will be raising. 
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number can not be empty', show_result=False, action_name='save', developer_name='Turan')
        elif not phone_number.isdecimal(): # This function will check if the number has at least one non-numeric character. If it has, again a massage will raise.
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='save', developer_name='Turan')
        # if everything is ok, whole those blocks will be passed, and we come here. 
        result_app = insert_person(name, phone_number)
        return render_template('add-update.html', show_result=True, result_html=result_app, not_valid=False, action_name='save', developer_name='Turan') #In addition, There is no message shown by user here. Thats why not valid is going to be False.
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='save', developer_name='Turan')

# Write a function named `update_record` which updates the record in the db using `GET` and `POST` methods,
# using template files named `add-update.html` given under `templates` folder
# and assign to the static route of ('update')
@app.route('/update', methods=['GET', 'POST'])
def update_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='update', developer_name='Turan')
        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number can not be empty', show_result=False, action_name='update', developer_name='Turan')
        elif not phone_number.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='update', developer_name='Turan')

        result_app = update_person(name, phone_number) #
        return render_template('add-update.html', show_result=True, result_html=result_app, not_valid=False, action_name='update', developer_name='Turan') #Again, There is no message shown by user here. Thats why not valid is going to be False.
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='update', developer_name='Turan')

# Write a function named `delete_record` which updates the record in the db using `GET` and `POST` methods,
# using template files named `delete.html` given under `templates` folder
# and assign to the static route of ('delete')
@app.route('/delete', methods=['GET', 'POST'])
def delete_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('delete.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, developer_name='Turan')
        result_app = delete_person(name)
        return render_template('delete.html', show_result=True, result_html=result_app, not_valid=False, developer_name='Turan') # In addition, There will be no message to be shown to the user here. Thats why not valid is going to be False.
    else:
        return render_template('delete.html', show_result=False, not_valid=False, developer_name='Turan')


# Add a statement to run the Flask application which can be reached from any host on port 80.
if __name__== '__main__':
    init_phonebook_db()
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80) 
