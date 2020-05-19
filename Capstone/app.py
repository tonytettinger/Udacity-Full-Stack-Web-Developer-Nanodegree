#!/usr/bin/env python3
import os
from flask import Flask, request, abort, jsonify
from models import setup_db, Movie, Actor
from flask_cors import CORS
from auth import AuthError, requires_auth
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    @app.route('/')
    def home_run():
        AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
        AUTH0_CALLBACK_URL = os.getenv("CALLBACK_URL")
        API_AUDIENCE = os.getenv("API_AUDIENCE")
        CLIENT_ID = os.getenv("CLIENT_ID")
        url = (
            f"https://{AUTH0_DOMAIN}/authorize"
            f"?audience={API_AUDIENCE}"
            f"&response_type=token&client_id="
            f"{CLIENT_ID}&redirect_uri="
            f"{AUTH0_CALLBACK_URL}"
        )
     
        return f"If the JWT tokens in the downloaded project folder expired please follow the README.txt for instructions and request new JWT tokens at this URL: {url}"
  
    @app.route('/movie', methods=['GET'])
    @requires_auth('get:movie')
    def get_movies(jwt):
        movies = Movie.query.all()
        if (len(movies) == 0):
            abort(404)
         
        def movie_json(movie):
            return{
                'id': movie.id,
                'title': movie.title,
                'release_date': movie.release_date
            }
        try:
            movie_list_json = [movie_json(movie) for movie in movies]
            return jsonify({
                'success': True,
                'movies': movie_list_json
            })
        except:
            abort(422)


    @app.route('/actor', methods=['GET'])
    @requires_auth('get:actor')
    def get_actors(jwt):
        actors = Actor.query.all()
        if (len(actors) == 0):
            abort(404)
            
        def actor_json(actor):
            return{
                'id': actor.id,
                'name': actor.name,
                'age': actor.age,
                'gender': actor.gender
            }
        try:
            actor_list_json = [actor_json(actor) for actor in actors]
            return jsonify({
                'success': True,
                'actors': actor_list_json
            })
        except:
            abort(422)

    @app.route('/movie', methods=['POST'])
    @requires_auth('post:movie')
    def add_movie(jwt):
     
        if not request.method == 'POST':
            abort(405)

        try:
            body = request.get_json()
            data = {
                'title': body['title'],
                'release_date': body['release_date']
            }

        except:
            abort(422)

        try:
            movie = Movie(**data)
            movie.insert()
            return jsonify(data)

        except:
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()
  
    @app.route('/movie/<int:delete_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(jwt, delete_id):
      
        to_delete = Movie.query.get(delete_id)
        if to_delete is None:
            abort(404)
        try:
            to_delete.deletes()
            return jsonify({
                'success': True,
                'delete': str(delete_id)
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
          
    @app.route('/movie/<int:patch_id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def patch_movie(jwt, patch_id):
        to_patch = Movie.query.filter(Movie.id == patch_id).one_or_none()
        if to_patch is None:
            abort(404)
        try:
            body = request.get_json()
            req_title = body.get("title")
            req_release_date = body.get("release_date")
            to_patch.title = req_title
            to_patch.release_date = req_release_date
            patched_movie = Movie.query.filter(Movie.id == patch_id).one_or_none()
            patched_movie_json = {
                'title': patched_movie.title,
                'release_date': patched_movie.release_date
            }
            return jsonify({
                'success': True,
                'movies': patched_movie_json
            })
       
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            
    # Error handling
       
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        'success': False,
        'error': 404,
        "message": "Resource Not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "unprocessable"
                        }), 422
    
    @app.errorhandler(AuthError)
    def auth_error(exception):
        return jsonify({
            "success": False,
            "error": exception.status_code,
            "message": exception.error['code']
        }), exception.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
