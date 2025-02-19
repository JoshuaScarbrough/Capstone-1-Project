import os
import requests
import random

from flask import Flask, render_template, redirect, flash, get_flashed_messages, session
from flask_debugtoolbar import DebugToolbarExtension

from forms import registerForm, loginForm, userMoodForm, userScheduleForm, userScheduleFormEdit, userGoalForm, userStepForm, userGoalsEdit, userStepEdit, userToDoTask, userToDoTaskEdit
from models import db, connect_db, User, Schedule, Task, Goal, Step, TodoTask, Verse
from datetime import date, timedelta

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:football8114@localhost:5432/capstone1
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.swovvcjjzcveduuikumr:5918scarfootball8114@aws-0-us-east-2.pooler.supabase.com:5432/capstone1'
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:5918scarfootball8114@db.swovvcjjzcveduuikumr.supabase.co:5432/capstone1"

# app.config['SQLALCHEMY_DATABASE_URI'] ="user=postgres.swovvcjjzcveduuikumr password=5918scarfootball8114 host=aws-0-us-east-2.pooler.supabase.comport=5432 dbname=capstone1"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

"""Connects our db to our app.py"""
connect_db(app)
ctx = app.app_context()
ctx.push()
db.create_all()


"""
This section of routes are my set up routes. The home page, register, login, and logout routes. 
After these routes you will be able to go into the application and use its features.
The login and register routes encorperate @classmethods that were implemented in the models.py.
These @classmethods are register and authenticate. We also store the users user.id in a session 
to be sure there is some resistance when trying to jump between routes without being logged in.  
"""

""" Route for home page """
@app.route('/')
def webLandingPage():
    return render_template('homePage.html')

"""Route for regestering"""
@app.route('/register', methods=["GET", "POST"])
def register():
    """ Regestering for the site / Creating your account """

    form = registerForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data

        """ .resister makes sure the passwords go through bcrypt """
        newUser = User.register(username=username, password=password, first_name=first_name, last_name=last_name, email=email )
        db.session.add(newUser)
        db.session.commit()

        """ Stores the user_id in a session """
        session["user_id"] = newUser.id
        return redirect(f'/users/mood/{newUser.username}')
    else:
        return render_template('register.html', form=form)

"""Route for login"""
@app.route('/login', methods=["GET", "POST"])
def login():
    """ Regestering for the site / Creating your account """

    form = loginForm()

    if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            """ .authenticate logges the user in and makes sure they have inserted a correct username and password """
            user = User.authenticate(username, password)

            """ Stores the user_id in a session """
            if user:
                session["user_id"] = user.id
                return redirect(f"/users/mood/{username}")
            else:
                form.username.errors = ["Bad name/password"]

    return render_template('login.html', form=form)

"""Route for logout"""
@app.route("/logout")
def logout():
    """ Logout meaning taking the user_id out of the session"""

    session.pop("user_id")

    return redirect("/login")




""" 
This section of routes is for the users home page and getting their mood for the user home page functionality.
It encorperates the users schedule, goals, and todo list. It is unique and is the page that the user will see all of their 
upcoming events. 
"""

@app.route('/users/mood/<username>', methods=["GET", "POST"])
def mood(username):
    """ Asking the mood of the User so that the site can populate a bible scripture that matches the situation"""
    
    """ Gets the user out of the database"""
    user = db.one_or_404(db.select(User).filter_by(username=username))
    user_username = user.username;

    form = userMoodForm(obj=user)

    if form.validate_on_submit():
        """ assigns the user mood to the user """
        user.user_mood = form.user_mood.data;
        db.session.commit()
        return redirect(f'/users/{user_username}')
    
    """ 
    checks to make sure that the user is logged in before they try and go to any other route inside of the webpage.
    This is for the security of the users information also just in case the database data was hacked into and the users 
    username was stolen and was trying to be used.
    """
    if "user_id" not in session:
        flash("You must be logged in to view")
        return redirect("/login")
    else:
        return render_template('userPageMood.html', user=user, form=form)

""" The users home page"""
@app.route('/users/<username>', methods=["GET", "POST"])
def userHomePage(username):
    """ Landing home page for the user"""

    user = db.one_or_404(db.select(User).filter_by(username=username))

    """ This is used to bring about all the tables that the user needs to see for their upcoming tasks """
    all_tasks = Task.query.filter_by(user_id=user.id).all()
    all_tasks_todo = TodoTask.query.filter_by(id=TodoTask.id).all()
    all_goals = Goal.query.filter_by(user_id=user.id).all()


    """ Calcuate Consecutive Days. This is so that the users can keep up with their progress and consistency """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    consecutive_days = 1

    if today == tomorrow:
        consecutive_days = consecutive_days + 1
        today = tomorrow
    
    if today > tomorrow:
        consecutive_days = 1

    

    """
    This section of the code is so that we can have some customizaion on the users page. It is used to bring back information
    that is unique to the specific day of the week that it is. 
    """
    today = date.today()
    day_number = today.weekday()

    """ Calculate day for Schedule """
    day = ""
    if day_number == 0:
        day = "Monday"
    elif day_number == 1:
        day = "Tuesday"
    elif day_number == 2:
        day = "Wednesday"
    elif day_number == 3:
        day = "Thursday"
    elif day_number == 4:
        day = "Friday"
    elif day_number == 5:
        day = "Saturday"
    elif day_number == 6:
        day = "Sunday"


    """ 
    This is our API request! In this section we pair withinformation inside of our database to get random 
    verses that are determinate upon the mood of the user. The random.randint helps us get this randomization
    """
    
    """ Importing our API base url """
    url = "https://bible-api.com/"

    "Handle rand number"
    random_int_up = random.randint(1,6)
    random_int_middle = random.randint(7,9)
    random_int_down = random.randint(10,15)

    "Get rand verse"
    verse_UP = Verse.query.get(random_int_up).verse
    verse_MIDDLE = Verse.query.get(random_int_middle).verse
    verse_DOWN = Verse.query.get(random_int_down).verse

    "user mood"
    user_mood = User.query.get(user.id).user_mood

    """ The names of the specific parts of the api that we need. We have to declare them as empty strings 
    outside of the if statements so that they update every time the users scripture changes and also so that 
    we dont get errors when certain moods arent chosen.
    """
    book = ""
    chapter = ""
    the_verse = ""
    user_verse = ""

    """ 
    This section of code handles the users mood and brings the api into effect. Based upon the users mood we get a 
    random verse from the database and combine the text with the base api url.
    """
    if user_mood == 'Joyful' or user_mood == 'Eager' or user_mood == 'Surprised':
        " combines the base url with the url endpoint stored in the models"
        response = requests.get(f'{url}{verse_UP}')
        " This part is so important because we need the response to be json so that we can comb through the dictionary "
        verse = response.json()
        book = (verse['verses'][0]['book_name'])
        chapter = (verse['verses'][0]['chapter'])
        the_verse = (verse['verses'][0]['verse'])
        user_verse = (verse['verses'][0]['text'])
    elif user_mood == 'Uncertain':
        response = requests.get(f'{url}{verse_MIDDLE}')
        verse = response.json()
        book = (verse['verses'][0]['book_name'])
        chapter = (verse['verses'][0]['chapter'])
        the_verse = (verse['verses'][0]['verse'])
        user_verse = (verse['verses'][0]['text'])
    elif user_mood == 'Angry' or user_mood == 'Disgusted' or user_mood == 'Sad':
        response = requests.get(f'{url}{verse_DOWN}')
        verse = response.json()
        book = (verse['verses'][0]['book_name'])
        chapter = (verse['verses'][0]['chapter'])
        the_verse = (verse['verses'][0]['verse'])
        user_verse = (verse['verses'][0]['text'])

    if "user_id" not in session:
        flash("You must be logged in to view")
        return redirect("/login")
    else:
        return render_template('userPage.html', user=user, today=today, consecutive_days=consecutive_days, day_number=day_number, day=day, all_tasks=all_tasks, all_tasks_todo=all_tasks_todo, all_goals=all_goals, book=book,chapter=chapter, the_verse=the_verse, user_verse=user_verse)




"""
    These are the main routes for the User and their page functionality. This is how the user will customize their application 
    to be able to add in a schedule, to do list, and goals. 
"""
@app.route('/users/ScheduleMaker/<username>', methods=["GET", "POST"])
def userSchedule(username):
    """ Allows the user to make a schedule for themselves """
     
    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_tasks = Task.query.filter_by(user_id=user.id).all()
    
    form = userScheduleForm()

    if form.validate_on_submit():
        all_tasks = Task.query.filter_by(user_id=user.id).all()
        user_id = user.id
        timestamp = form.timestamp.data
        day_of_week = form.days_of_week.data
        entry= form.entry.data

        schedule = Schedule(user_id=user_id)
        task = Task(timestamp=timestamp, day=day_of_week, entry=entry, user_id=user_id)

        db.session.add(schedule)
        db.session.add(task)
        db.session.commit()
        form = userScheduleForm(formdata=None)
        return render_template('userScheduleSaved.html', user=user, all_tasks=all_tasks, form=form)

    if "user_id" not in session:
        flash("You must be logged in to view")
        return redirect("/login")
    else:
        return render_template('userScheduleMaker.html', user=user, all_tasks=all_tasks, form=form)

@app.route('/users/ScheduleFull/<username>')
def userScheduleFull(username):
    """ Allows the user to see their full schedule """

    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_tasks = Task.query.filter_by(user_id=user.id).all()

    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('userScheduleFull.html', user=user, all_tasks=all_tasks)

@app.route('/users/EditDay/<username>', methods=["GET", "POST"])
def EditDay(username):
    """ Allows the user to edit the schedule specific to the day they need edited """

    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_tasks = Task.query.filter_by(user_id=user.id).all()

    form = userScheduleFormEdit()

    if form.validate_on_submit():
        all_tasks = Task.query.filter_by(user_id=user.id).all()
        task = form.task_id.data

        Task.query.filter(Task.id == task).delete()
        db.session.commit()
        return redirect(f'/users/ScheduleMaker/{username}')
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('editDay.html', user=user, all_tasks=all_tasks, form=form)


""" These are going to be my routes for the Users Goals """
@app.route('/users/Goals/<username>', methods=["GET", "POST"])
def Goals(username):
    """ allows the user to make goals for themselves """
    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_goals = Goal.query.filter_by(user_id=user.id).all()

    form = userGoalForm()

    if form.validate_on_submit():
        user_id = user.id
        goal_code = form.goal_code.data
        goal = form.goal.data

        goal = Goal(user_id = user_id , goal_code = goal_code, goal = goal)
        db.session.add(goal)
        db.session.commit()
        return redirect(f'/users/GoalPlan/{username}')
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('userGoals.html', all_goals=all_goals, user=user, form=form)

@app.route('/users/GoalPlan/<username>', methods=["GET", "POST"])
def GoalPlan(username):
    """ user creates a plan to ahieve those goals"""

    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_goals = Goal.query.filter_by(user_id=user.id).all()
    all_steps = Step.query.filter_by(id=Step.id).all()

    form = userStepForm()

    if form.validate_on_submit():
        goal_id = form.goal_id.data
        step = form.step.data
        end_date = form.end_date.data

        step = Step(goal_id=goal_id, step=step, end_date=end_date)
        db.session.add(step)
        db.session.commit()
        return render_template('userStepSaved.html', user=user)
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
         return render_template('userGoalsPlan.html', user=user, all_goals=all_goals, all_steps=all_steps, form=form)

@app.route('/users/EditGoals/<username>', methods=["GET", "POST"])
def EditGoals(username):
    """ Edit the goals you have made"""
     
    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_goals = Goal.query.filter_by(user_id=user.id).all()
    all_steps = Step.query.filter_by(id=Step.id).all()

    
    form = userGoalsEdit()

    if form.validate_on_submit():
        all_goals = Goal.query.filter_by(user_id=user.id).all()
        all_steps = Step.query.filter_by(id=Step.id).all()
        goal = form.goal_id.data

        Step.query.filter(Step.goal_id == goal).delete()
        Goal.query.filter(Goal.id == goal).delete()
        db.session.commit()
        return redirect(f'/users/Goals/{username}')
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
         return render_template('editGoal.html', user=user, all_goals=all_goals, all_steps=all_steps, form=form)

@app.route('/users/EditSteps/<username>', methods=["GET", "POST"])
def EditGoalPlan(username):
    """ Edit the steps you have made for those goals """
     
    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_goals = Goal.query.filter_by(user_id=user.id).all()
    all_steps = Step.query.filter_by(id=Step.id).all()

    form = userStepEdit()

    if form.validate_on_submit():
        all_steps = Step.query.filter_by(id=Step.id).all()
        step = form.step_id.data

        Step.query.filter(Step.id == step).delete()
        db.session.commit()
        return redirect(f'/users/GoalPlan/{username}')
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('editStep.html', user=user, all_goals=all_goals, all_steps=all_steps, form=form)


""" Routes for the To-DO List"""
@app.route('/users/ToDoTask/<username>', methods=["GET", "POST"])
def ToDoTask(username):
    """ User creates their todo list"""

    user = db.one_or_404(db.select(User).filter_by(username=username))
    all_tasks = TodoTask.query.filter_by(id=TodoTask.id).all()

    form = userToDoTask()

    if form.validate_on_submit():
        user_id = user.id
        date_due = form.date_due.data
        time = form.time.data
        entry = form.entry.data

        task = TodoTask(user_id=user_id, date_due=date_due, time=time, entry=entry)
        db.session.add(task)
        db.session.commit()
        return render_template('userToDoTaskSaved.html', user=user)
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('userToDoTask.html', user=user, all_tasks=all_tasks, form=form)

@app.route('/users/EditToDoTasks/<username>', methods=["GET", "POST"])
def EditToDoTask(username):
    """ user can edit their tasks in the todo list """

    user = db.one_or_404(db.select(User).filter_by(username=username))
    
    form = userToDoTaskEdit()

    if form.validate_on_submit():
        task = form.task_id.data

        TodoTask.query.filter(TodoTask.id == task).delete()
        db.session.commit()
        return redirect(f'/users/ToDoTask/{username}')
    
    if "user_id" not in session:
            flash("You must be logged in to view")
            return redirect("/login")
    else:
        return render_template('editToDoTask.html', user=user, form=form)




""" This what allows our python app to run"""
#if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)
  #  app.run(debug=True)
    
