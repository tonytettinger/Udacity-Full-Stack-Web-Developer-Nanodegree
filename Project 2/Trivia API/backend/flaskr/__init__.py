import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  @app.route('/categories')
  def get_categories():
      query_categories = Category.query.all()
      categories_dict = {}
      for row in query_categories:
        categories_dict[row.id] = row.type
      
      return jsonify({'categories': categories_dict})

  '''
  @TODO: 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

#helper function to convert the query results to a dict for sending back in a JSON format
  def convert_questions_to_dict(query):
    questions_list = []

    for row in query:
        current_question = {
          'id' : row.id,
          'question' : row.question,
          'answer' : row.answer,
          'category' : row.category,
          'difficulty' : row.difficulty
        }
        questions_list.append(current_question)
    return questions_list


  @app.route('/questions', methods=['GET'])
  def get_questions():
      page = int(request.args.get('page')) - 1
      query_all = Question.query
      query_count = query_all.count()
      query_categories = Category.query.all()

      if len(query_categories) == 0:
        abort(404)

      questions_current_page = query_all.limit(10).offset(page)
      
      categories_dict = {}
      for row in query_categories:
        categories_dict[row.id] = row.type

      answer =  {
          'questions': convert_questions_to_dict(questions_current_page),
          'totalQuestions': query_count,
          'categories': categories_dict
          }
      
      return jsonify(answer)

  @app.route('/questionsDelete/<int:delete_id>', methods=['DELETE'])
  def delete_question(delete_id):
    if not request.method == 'DELETE':
      abort(405)
    body = request.get_json()
    currentCategory = body['currentCategory']
    question_to_delete = Question.query.get(delete_id)
    if question_to_delete is None:
      abort(404)
    question_to_delete.deletes()
    question = convert_questions_to_dict(Question.query.filter_by(category=currentCategory))

    return jsonify({
      'success': True,
      'question' : question
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questionsPost', methods=['POST'])
  def post_question():
      body = request.get_json()
      data = {
        'question': body['question'],
        'answer': body['answer'],
        'category': body['category'],
        'difficulty': body['difficulty']
      }

      for key in data:
        if not data[key]:
          abort(422)

      question = Question(**data)
      question.insert()
    
      result = {
        'success': True,
      }
      return jsonify(data)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questionsSearch', methods=['POST'])
  def search_questions():
      body = request.get_json()
      search_term = body['searchTerm']
      search_query = Question.query.filter(Question.question.ilike('%' + search_term + '%'))

      questions = convert_questions_to_dict(search_query)
      return jsonify({
          'questions': questions,
          'totalQuestions': len(questions),
          'currentCategory': 'None'
          })
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    filtered_by_cat_questions = Question.query.filter(Question.category == category_id).all()
    questions = []
    for row in filtered_by_cat_questions:
        current_question = {
          'id' : row.id,
          'question' : row.question,
          'answer' : row.answer,
          'category' : row.category,
          'difficulty' : row.difficulty
        }
        questions.append(current_question)
    return jsonify({
          'questions': questions,
          'totalQuestions' : len(questions),
          'current_category': questions[0]['category']
          })
 

  '''
  @TODO: 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def quizzes_search():
    body = request.get_json()
    previous_questions = body['previous_questions']
    quiz_category = body['quiz_category']
    quiz_category_id = quiz_category['id']
    filtered_question = Question.query.filter(Question.category == quiz_category_id).filter(~Question.id.in_(previous_questions)).first()

    filtered_q_as_d = filtered_question.__dict__
    current_question = {}
    current_question['question'] = filtered_q_as_d['question']
    current_question['answer'] = filtered_q_as_d['answer']
    current_question['id'] = filtered_q_as_d['id']

    return jsonify({
          'question' : current_question
        })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error' : 404,
      "message" : "Resource Not found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      'success': False,
      'error' : 405,
      "message" : "Not Allowed"
    }), 405
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error' : 422,
      "message" : "Unprocessable"
    }), 422

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success': False,
      'error' : 400,
      "message" : "Not found"
    }), 400
  
  return app

    