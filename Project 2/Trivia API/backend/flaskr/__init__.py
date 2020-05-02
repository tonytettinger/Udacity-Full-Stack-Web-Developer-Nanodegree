import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


db = SQLAlchemy()
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

    if not request.method == 'GET':
      abort(405)  

    try:
      page = int(request.args.get('page')) - 1

    except:
      abort(400) 
    query_all = Question.query

    if query_all is None:
      abort(404)
    query_count = query_all.count()
    query_categories = Category.query.all()

    if len(query_categories) == 0:
      abort(404)

    try:
      questions_current_page = query_all.limit(10).offset(page)
      
      categories_dict = {}
      for row in query_categories:
        categories_dict[row.id] = row.type

      answer =  {
          'questions': convert_questions_to_dict(questions_current_page),
          'totalQuestions': query_count,
          'categories': categories_dict
          }
      db.session.commit()   
      return jsonify(answer)

    except:
      db.session.rollback()
      abort(422)

    finally: 
      db.session.close()

  @app.route('/questionsDelete/<int:delete_id>', methods=['DELETE'])
  def delete_question(delete_id):

    if not request.method == 'DELETE':
      abort(405)

    body = request.get_json()
    currentCategory = body['currentCategory']
    question_to_delete = Question.query.get(delete_id)

    if question_to_delete is None:
      abort(404)

    try:
      question_to_delete.deletes()
      question = convert_questions_to_dict(Question.query.filter_by(category=currentCategory))
      db.session.commit()
      return jsonify({
        'status' : 200,
        'success': True,
        'question' : question
      })

    except:
      db.session.rollback()
      abort(422)

    finally:
      db.session.close()

  @app.route('/questionsPost', methods=['POST'])
  def post_question():

    if not request.method == 'POST':
      abort(405)

    try:
        body = request.get_json()
        data = {
          'question': body['question'],
          'answer': body['answer'],
          'category': body['category'],
          'difficulty': body['difficulty']
        }

    except:
        abort(422)

    try:
      question = Question(**data)
      question.insert()
      return jsonify(data)

    except:
        db.session.rollback()
        abort(422)

    finally:
        db.session.close()


  @app.route('/questionsSearch', methods=['POST'])
  def search_questions():

    if not request.method == 'POST':
      abort(405)

    try:
      body = request.get_json()
      search_term = body['searchTerm']

    except: 
      abort(422)
      db.session.rollback()
    
    search_query = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

    if search_query == []:
      abort(404)

    try:
      questions = convert_questions_to_dict(search_query)
      return jsonify({
          'questions': questions,
          'totalQuestions': len(questions)
          })

    except:
      abort(422)
      db.session.rollback()

    finally:
      db.session.close()
    

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    if not request.method == 'GET':
      abort(405)

    filtered_by_cat_questions = Question.query.filter(Question.category == category_id).all()
    if len(filtered_by_cat_questions) == 0:
      abort(404)
    
    try:
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
      db.session.commit()
      return jsonify({
          'questions': questions,
          'totalQuestions' : len(questions),
          'current_category': questions[0]['category']
          })
    except:
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()


  @app.route('/quizzes', methods=['POST'])
  def quizzes_search():

    if not request.method == 'POST':
      abort(405)

    try:
      body = request.get_json()
      previous_questions = body['previous_questions']
      quiz_category = body['quiz_category']
      quiz_category_id = quiz_category['id']

    except:
      abort(422)
    
    if quiz_category['id'] == 0:
      filtered_question = Question.query.filter(~Question.id.in_(previous_questions)).first()
      
    else:
      filtered_question = Question.query.filter(Question.category == quiz_category_id).filter(~Question.id.in_(previous_questions)).first()

    try:
      filtered_dict = filtered_question.__dict__
      print(filtered_question)
      current_question = {}
      current_question['question'] = filtered_dict['question']
      current_question['answer'] = filtered_dict['answer']
      current_question['id'] = filtered_dict['id']

      print(current_question)
      return jsonify({
            'question' : current_question
          })

    except:
      db.session.rollback()
      abort(422)

    finally:
      db.session.close()

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
  def bad_request(error):
    return jsonify({
      'success': False,
      'error' : 400,
      "message" : "Bad Request"
    }), 400
  
  return app

    