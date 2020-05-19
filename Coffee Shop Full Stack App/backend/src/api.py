import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app,resources={r"*": {"origins": "*"}})
# CORS Headers 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH, OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if (len(drinks) == 0):
        abort(404)
    try:
        drinks_list_json = [drink.short() for drink in drinks]
        print(drinks_list_json)
        return jsonify({
            'success': True,
            'drinks': drinks_list_json
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    all_drinks = Drink.query.all()
    if (len(all_drinks) == 0):
        abort(404)
    try:
        long_drinks_list_json = [drink.long() for drink in all_drinks]
        print(long_drinks_list_json)
        return jsonify({
            'success': True,
            'drinks': long_drinks_list_json
        })
    except:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    try:
        body = request.get_json()
        req_title = body['title']
        req_recipe = json.dumps(body['recipe'])
        drink = Drink(title=req_title, recipe=req_recipe)
        drink.insert()
        new_drink = Drink.query.filter(Drink.title == req_title).one_or_none()
        print(new_drink)
        new_drink_long = new_drink.long()
        return jsonify({
            'success': True,
            'drink': new_drink_long
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()

@app.route('/drinks/<int:patch_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, patch_id):
    to_patch = Drink.query.filter(Drink.id == patch_id).one_or_none()
    print(to_patch)
    if (to_patch == False):
        abort(404)
    try:
        body = request.get_json()
        req_title = body['title']
        req_recipe = body['recipe']
        req_recipe = json.dumps(req_recipe)
        to_patch.title = req_title
        to_patch.recipe = req_recipe
        to_patch.update()
        patched_drink = Drink.query.filter(Drink.id == patch_id).one_or_none()
        print(patched_drink)
        patched_drink_long = patched_drink.long()
        print(patched_drink_long)
        return jsonify({
            'success': True,
            'drink': patched_drink_long
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()

@app.route('/drinks/<int:delete_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, delete_id):
    try:
        to_delete = Drink.query.get(delete_id)
        to_delete.delete()
        print(delete_id)
        return jsonify({
            'success': True,
            'delete': str(delete_id)
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      "message": "Resource Not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(exception):
    return jsonify({
    "success": False,
    "error": exception.status_code,
    "message": exception.error['code']
    }), 401