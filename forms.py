import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, TextAreaField, SelectField, TimeField, SelectMultipleField, DateField, validators
from wtforms.validators import DataRequired, Email, Length


""" Register and Login Forms """
class registerForm(FlaskForm):
    """ Form for registering users"""

    first_name = StringField('First name:', validators=[DataRequired()])
    last_name = StringField('Last name:', validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[Length(min=6)])
    email = StringField('E-mail:', validators=[DataRequired(), Email()])


class loginForm(FlaskForm):
    """ Form for logging in users"""

    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[Length(min=6)])

""" User Mood"""
class userMoodForm(FlaskForm):
    """ Asks the specific mood of a user """

    user_mood = SelectField('Mood', choices=[("Joyful"), ("Surprised"), ("Eager"), ("Uncertain"), ("Angry"), ("Disgusted"), ("Sad")],  validators=[DataRequired()])

""" User Schedule Creation """
class userScheduleForm(FlaskForm):
    """  Asks questions for the user to be able to create a schedule for themselves """

    days_of_week = SelectMultipleField('Select the days of the Week', choices=[("Monday"), ("Tuesday"), ("Wednesday"), ("Thursday"), ("Friday"), ("Saturday"), ("Sunday")],  validators=[DataRequired()])
    timestamp = IntegerField('Time of Task', [validators.NumberRange(min=0000, max=2400)])
    entry = TextAreaField('Task for this day', render_kw={"rows": 1, "cols": 10})

class userScheduleFormEdit(FlaskForm):
    """ Edit the schedule """

    task_id = IntegerField(' ID of the task you would like to delete')


""" User Goals Creation """
class userGoalForm(FlaskForm):
    """ Ask questions so that the user can have goals """

    goal_code = StringField('Short (short) or Long (long) Term Goal', validators=[DataRequired()])
    goal = TextAreaField('What is your Goal?', render_kw={"rows": 1, "cols": 10})

class userStepForm(FlaskForm):
    """ Develop a plan for the goals you have """

    goal_id = IntegerField('Insert the Goal ID', validators=[DataRequired()])
    step = TextAreaField('Step to achieving goal', render_kw={"rows": 1, "cols": 20}, validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d')

class userGoalsEdit(FlaskForm):
    """ Edit the schedule """

    goal_id = IntegerField('ID of the Goal you would like to delete')

class userStepEdit(FlaskForm):
    """ Edit the schedule """

    step_id = IntegerField('ID of the Step you would like to delete')

class userToDoTask(FlaskForm):
    """ Create a Task for todo list """

    date_due = DateField('Date of completion', format='%Y-%m-%d')
    time = TimeField('Time task needs to be accomplished', validators=[DataRequired()])
    entry = TextAreaField('Task', render_kw={"rows": 1, "cols": 10})

class userToDoTaskEdit(FlaskForm):
    """ Edit the schedule """

    task_id = IntegerField('ID of the Task you would like to delete')