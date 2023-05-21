from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# __name__ is an env variable that refers to the name of the application's package
app = Flask(__name__)
# tells app where our database is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.database'
#Initialize the database
database = SQLAlchemy(app)

#The outline of every Task entry in our database
class Task(database.Model):
    #Each variable is a Column object of different types and default values
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(200), nullable=False)
    # Will be set automatically to the time it was created
    date_created = database.Column(database.DateTime , default=datetime.utcnow)

    # Every time we create a new element, returns the id number
    # Acts like the __str__ function in this case
    def __repr__(self):
        return '<Task %r>' % self.id

#route() decorator to tell Flask what URL should trigger our function
#POST tells we can send data to our database, GET means we can retrieve data
@app.route('/', methods=['POST', 'GET'])
# function renders the file we want, automatically searches for it in the templates file
def index():
    if request.method == 'POST':
        #Grabs the content from the form request
        task_content = request.form['content']
        #Create new Task object from the form content
        new_task = Task(content=task_content)

        try:
            #Push new task to database
            database.session.add(new_task)
            database.session.commit()
            #Redirect back to our index (basically calls GET / again)
            return redirect('/')
        except:
            #Error message, automatically formatted in HTML
            return 'Issue occurred adding your task'
    else:
        #Grabs all the entries, orders them, and returns them all
        tasks = Task.query.order_by(Task.date_created).all()
        return render_template('index.html', iterable_tasks=tasks)

#Triggered by delete button
@app.route('/delete/<int:task_id>')
def delete(task_id):
    # Gets the Task object based on the task_id that was passed
    task_to_delete = Task.query.get_or_404(task_id)

    try:
        # Deletes the task from database
        database.session.delete(task_to_delete)
        database.session.commit()
        # Redirects back to our index
        return redirect('/')
    except:
        return 'Error occurred deleting task'

#Triggered by update button
@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update(task_id):
    # Grabs Task object we're going to update
    task_to_update = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        #Change the content with the form's content
        task_to_update.content = request.form['content']

        #Update changes and go back to index.html
        try:
            database.session.commit()
            return redirect('/')
        except:
            return 'Error occurred updating task'
    else:
        return render_template('update.html', task=task_to_update)
# Needed for running on terminal
if __name__ == "__main__":
    app.run(debug=True)

# If database isn't working, do the following:
# python3
# from app import app, database
# app.app_context().push()
# database.create_all()
# exit()