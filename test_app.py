from app import app
from models import db, User
from flask import session
from unittest import TestCase


app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CRSF_ENABLED'] = False

"""
class for testing all get request per route
class for texting all post request per route
class for testing all redirects
class for testing functionality of schedulemaker,
"""

class getRequestTest(TestCase):

    def test_base_route(self):
        with app.test_client() as client:
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1> Accountabilit-E </h1>', html)

    def test_register_route(self):
        with app.test_client() as client:
            res = client.get('/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Register</h1>', html)

    def test_login_route(self):
        with app.test_client() as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Login</h1>', html)


class testRedirects(TestCase):
    def test_mood_redirect_route(self):
        with app.test_client() as client:
            res = client.get(f'/users/mood/testUser')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, '/login')

    def test_userHomepage_route(self):
        with app.test_client() as client:
            res = client.get('/users/testUser')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, '/login')

    def test_userEditSteps_route(self):
        with app.test_client() as client:
            res = client.get('/users/EditSteps/testUser')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, '/login')



class SessionTesting(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    def test_mood_session_value(self):
        with self.app.session_transaction() as session:
            session['user_id'] = 1

        response = self.app.get('/users/mood/testUser')  
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h2> How are you feeling today? </h2>', response.data)

    def test_userHomepage_session_value(self):
        with self.app.session_transaction() as session:
            session['user_id'] = 1

        response = self.app.get('/users/testUser')  
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<p> testUser  (Logged in!) </p>', response.data)

    def test_userScheduleMaker_session_value(self):
        with self.app.session_transaction() as session:
            session['user_id'] = 1

        response = self.app.get('/users/ScheduleMaker/testUser')  
        self.assertEqual(response.status_code, 200)
        self.assertIn(b' <h1>test User\'s Schedule </h1>', response.data)



class SessionTestingPostRequests(TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_post_request_scheduleMaker_in_session(self):
        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 1
                
            # Simulate form data
            form_data = {
                'timestamp': '0500',
                'day_of_week': 'Monday',
                'entry': 'Task'
            }
            
            
            response = c.post('/users/ScheduleMaker/testUser', data=form_data, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)


    def test_post_request_goals_in_session(self):
        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 1
                
            # Simulate form data
            form_data = {
                'user_id' : 1,
                'goal_code': 1,
                'goal': 'test'
            }
            
            
            response = c.post('/users/Goals/testUser', data=form_data, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
