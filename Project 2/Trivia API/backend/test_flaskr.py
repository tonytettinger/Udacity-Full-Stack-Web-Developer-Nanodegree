import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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

    def test_post_new_question(self):
        data = {
            'question': 'what?',
            'answer': 'yes',
            'category': 3,
            'difficulty': 2,
        }
        question = Question(**data)
        question.insert()
        question_return = Question.query.filter_by(question='what?')
        current_question = {}
        for row in question_return:
            current_question = {
                'question' : row.question,
                'answer' : row.answer,
                'category' : row.category,
                'difficulty' : row.difficulty
            }
        self.assertDictEqual(current_question, data)
        question_return.delete()

    def test_delete_question(self):
        data = {
            'question': 'whatsupd?',
            'answer': 'yes',
            'category': 3,
            'difficulty': 2,
        }
        question = Question(**data)
        question.insert()
        question_return = Question.query.filter_by(question='whatsupd?').first()
        question_id = question_return.__dict__['id']
        question_id_str = str(question_id)

        res = self.client().delete('/questionsDelete/97')

        self.assertEqual( None, question_id_str)


        


        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()