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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
      query_categories = Category.query.all()
      categories_dict = {}
      for row in query_categories:
        categories_dict[row.id] = row.type
      
      return jsonify({'categories': categories_dict})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
      page = int(request.args.get('page')) - 1
      query_all = Question.query
      query_categories = Category.query.all()

      if len(query_categories) == 0:
        abort(404)

      questions_current_page = query_all.limit(10).offset(page)
      question_total = Question.query.count() 
      questions_list = []
      categories_dict = {}
      for row in query_categories:
        categories_dict[row.id] = row.type

      for row in questions_current_page:
        current_question = {
          'id' : row.id,
          'question' : row.question,
          'answer' : row.answer,
          'category' : row.category,
          'difficulty' : row.difficulty
        }
        questions_list.append(current_question)

      answer =  {
          'questions': questions_list,
          'totalQuestions': question_total,
          'categories': categories_dict,
          'currentCategory': questions_list[0]['category'] 
          }
      
      return jsonify(answer)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questionsDelete/<int:delete_id>', methods=['DELETE'])
  def delete_question(delete_id):
    Question.query.filter_by(id=delete_id).delete()

    return jsonify(result = {
      'success': True,
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
    
      question = Question(**data)
      question.insert()
    
      result = {
        'success': True,
      }
      return jsonify(result)


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
      questions_list = []

      search_query = Question.query.filter(Question.question.ilike('%' + search_term + '%'))
      for row in search_query:
        current_question = {
          'id' : row.id,
          'question' : row.question,
          'answer' : row.answer,
          'category' : row.category,
          'difficulty' : row.difficulty
        }
        questions_list.append(current_question)

      return jsonify({
          'questions': questions_list,
          'totalQuestions': len(questions_list),
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
          'total_questions' : len(questions),
          'current_category': questions[0]['category']
          })
 

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

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
    
    if filtered_question == None:
      return jsonify({
          'question' : None
        })
    filtered_q_as_d = filtered_question.__dict__
    current_question = {}
    current_question['question'] = filtered_q_as_d['question']
    current_question['answer'] = filtered_q_as_d['answer']
    current_question['id'] = filtered_q_as_d['id']

    return jsonify({
          'question' : current_question
        })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error' : 404,
      "message" : "Resource Not found"
    }), 404
  
  @app.errorhandler(422)
  def not_found(error):
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

    