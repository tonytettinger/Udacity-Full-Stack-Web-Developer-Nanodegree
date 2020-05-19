import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


def query_to_dict(query):
    query_dict = query.__dict__
    result_dict = {
            'question': query_dict['question'],
            'answer': query_dict['answer'],
            'category': query_dict['category'],
            'difficulty': query_dict['difficulty']
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
    if query is not None:
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
        self.test_post = {
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
    TEST: Endpoint GET /questions?page=1
    """

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        question_data = json.loads(res.data)
        self.assertEqual(len(question_data['questions']), 10)
        delete_test_post()

    def test_get_questions_400(self):
        response = self.client().get('/questions?page=x')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_response_data["error"], 400)
        delete_test_post()

    '''
    TEST:  Endpoint DELETE /questionsDelete/<int:post_id>
    When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    def test_delete_question(self):
        insert_test_post()
        post = query_test_post()
        post_id = post.id

        # Check the post exists before deleting
        self.assertIsNotNone(post)
        delete_json = {
            'currentCategory' : 3
        }
        # Click on the trash icon
        self.client().delete(f"/questionsDelete/{post_id}", data=json.dumps(delete_json), content_type='application/json')
        # Removal persist in the database
        deleted = Question.query.get(post_id)
        self.assertIsNone(deleted)
    """
    TEST: Endpoint DELETE /questionsDelete/<int:post_id>, 405 
    Method Not Allowed when requesting delete using wrong method.
    """
    def test_delete_wrong_method_error_handling(self):
        insert_test_post()
        post = query_test_post()
        # Check the post exists before deleting
        self.assertIsNotNone(post)

        # Click on the trash icon
        response = self.client().get(f"/questionsPost", data=json.dumps(self.test_post), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json_response_data["error"], 405)
        delete_test_post()

    '''
    TEST: Endpoint POST /questionsPost
    '''
    def test_post_question(self):
        self.client().post(f"/questionsPost", data=json.dumps(self.test_post), content_type='application/json')
        test_post = query_test_post()
        self.assertIsNotNone(test_post)
        delete_test_post()
    '''
    TEST: Endpoint POST /questionsPost, 422
    Missing submission field
    '''
    def test_post_question_422(self):
        wrong_post = self.test_post
        # Simulate missing answer 
        wrong_post.pop('answer')

        response = self.client().post(f"/questionsPost", data=json.dumps(wrong_post), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_response_data["error"], 422)
        delete_test_post()
    
    '''
    TEST: Endpoint POST /questionsSearch
    Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Using the phrase "Test Question" from the test data. 
    '''
    def test_search(self):
        insert_test_post()
        search_term = {
            'searchTerm': 'Test Question?'
        }
        # First do a search by SQL directly from the database
        questions_search_query = Question.query.filter_by(question="Test Question?").all()
        response = self.client().post(f"/questionsSearch", data=json.dumps(search_term), content_type='application/json')
        json_response_data = json.loads(response.data)
        # Check if the database query is the same length as the endpoint query
        self.assertEqual(len(json_response_data['questions']), len(questions_search_query))
        delete_test_post()

    '''
    TEST: Endpoint POST /questionsSearch, 404
    '''
    def test_search_404(self):
        insert_test_post()
        search_term = {
            'searchTerm': 'Not existing term'
        }

        response = self.client().post(f"/questionsSearch", data=json.dumps(search_term), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_response_data["error"], 404)
        delete_test_post()

    '''
    TEST: Endpoint GET /categories/<int:category_id>/questions 
    In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    def test_get_categories(self):
        insert_test_post()
        response = self.client().get("/categories/3/questions")
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        for data in json_response_data['questions']:
            self.assertEqual(data['category'], 3)
        delete_test_post()

    '''TEST: Endpoint GET /categories/<int:category_id>/questions, 404''' 

    def test_get_categories(self):
        insert_test_post()
        response = self.client().get("/categories/99/questions")
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_response_data["error"], 404)
        delete_test_post()

    '''TEST: Endpoint, POST  /quizzes'''

    def test_quizzes(self):
        insert_test_post()
        quizCategory = {'type': 'all', 'id': 0}
        quiz_post_data = {
            'previous_questions': [],
            'quiz_category': quizCategory
        }
        response = self.client().post("/quizzes", data=json.dumps(quiz_post_data), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_response_data), 1)
        delete_test_post()
    
    '''TEST: Endpoint, POST  /quizzes, 422 wrong category queried with no elements'''

    def test_quizzes(self):
        insert_test_post()
        quizCategory = {'type': 'all', 'id': 9999}
        quiz_post_data = {
            'previous_questions': [],
            'quiz_category': quizCategory
        }
        response = self.client().post("/quizzes", data=json.dumps(quiz_post_data), content_type='application/json')
        json_response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_response_data["error"], 422)
        delete_test_post()

# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()
