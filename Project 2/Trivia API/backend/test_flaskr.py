import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category

def query_to_dict(query):
        query_dict = query.__dict__
        result_dict = {
                'question' : query_dict['question'],
                'answer' : query_dict['answer'],
                'category' : query_dict['category'],
                'difficulty' : query_dict['difficulty']
        }
        return result_dict

def insert_test_post():
    data = {
        'question': 'Test Question?',
        'answer': 'Yes this is a test question.',
        'category': 3,
        'difficulty': 2,
    }
    question = Question(**data)
    question.insert()
    return data

def query_test_post():
    query = Question.query.filter_by(question="Test Question?").first()
    return query

def delete_test_post():
    query = Question.query.filter_by(question="Test Question?").first()
    query.deletes()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.test_post = data = {
        'question': 'Test Question?',
        'answer': 'Yes this is a test question.',
        'category': 3,
        'difficulty': 2,
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        question_data = json.loads(res.data)
        self.assertEqual(len(question_data['questions']), 10)

    '''
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    def test_delete_question(self):
        insert_test_post()
        post = query_test_post()
        post_id = post.id

        #Check the post exists before deleting
        self.assertIsNotNone(post)
        delete_json = {
            'currentCategory' : 3
        }
        #Click on the trash icon
        self.client().delete(f"/questionsDelete/{post_id}", data=json.dumps(delete_json), content_type='application/json')
        #Removal persist in the database
        deleted = Question.query.get(post_id)
        self.assertIsNone( deleted )
    """
    Test API responses with 405 Method Not Allowed when
    requesting delete using wrong method.
    """
    def test_delete_wrong_method_error_handling(self):
        insert_test_post()
        post = query_test_post()
        post_id = post.id

        #Check the post exists before deleting
        self.assertIsNotNone(post)
        delete_json = {
            'currentCategory' : 3
        }
        #Click on the trash icon
        response = self.client().get(f"/questionsDelete/{post_id}", data=json.dumps(delete_json), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json_response_data["error"], 405)
        delete_test_post()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()