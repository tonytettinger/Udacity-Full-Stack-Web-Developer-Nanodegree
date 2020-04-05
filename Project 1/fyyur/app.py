#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import config
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.sql import func
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
migrate.init_app(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'show'
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_description = db.Column(db.Boolean, default=False)
    shows_venue = db.relationship('Show', backref='venue')

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows_art = db.relationship('Show', backref='artist')

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  count_results = len(search_results)
  response = {}
  data = []

  today = datetime.now()
  today = today.strftime('%Y-%m-%d')
  def get_upcoming_number(venue_id):
    total = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time>today).all()
    return len(total)
  for result in search_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": get_upcoming_number(result.id)
    })
  response["count"] = count_results
  response["data"] = data
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  arr = venue.genres[1:-1] 
  arr = ''.join(arr).split(",")
  venue.genres = arr
  today = datetime.now()
  today = today.strftime('%Y-%m-%d')
  if venue.seeking_description:
    venue.seeking_text = "We are on the lookout for a local artist to play every two weeks. Please call us."
  
  #Query upcoming and past shows
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time>today).all()
  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time<today).all()
  #Function to get filtered shows data for display, past or upcoming
  def shows(shows):
    show_render_data = []
    shows_count = 0
    for show in shows:
      shows_count = shows_count+1
      show_render_data.append(
        {
          "start_time" : show.start_time,
          "artist_id" : show.artist_id,
          "artist_image_link" : show.artist.image_link,
          "artist_name" : show.artist.name
        }
      )
    return [shows_count, show_render_data]

  past_shows = shows(past_shows)
  upcoming_shows = shows(upcoming_shows)

  venue.past_shows_count = past_shows[0]
  venue.past_shows = past_shows[1]

  venue.upcoming_shows_count = upcoming_shows[0]
  venue.upcoming_shows = upcoming_shows[1]

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate():
      venue = Venue( 
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'], 
        phone=request.form['phone'],
        address=request.form['address'],
        genres=form.genres.data,
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'],
        website=request.form['website'],
        seeking_description=form.seeking_talent.data
        )
      db.session.add(venue)
      db.session.commit()
      return render_template('pages/home.html')
    else:
      return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count_results = len(search_results)
  response = {}
  data = []

  today = datetime.now()
  today = today.strftime('%Y-%m-%d')

  def get_upcoming_number(artist_id):
    total = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time>today).all()
    return len(total)
  for result in search_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": get_upcoming_number(result.id)
    })
  response["count"] = count_results
  response["data"] = data
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  arr = artist.genres[1:-1] 
  arr = ''.join(arr).split(",")
  artist.genres = arr
  today = datetime.now()
  today = today.strftime('%Y-%m-%d')
  if artist.seeking_venue:
    artist.seeking_text = "Looking for venue to play in."
  
  #Query upcoming and past shows
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time>today).all()
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time<today).all()
  #Function to get filtered shows data for display, past or upcoming
  def shows(shows):
    show_render_data = []
    shows_count = 0
    for show in shows:
      shows_count = shows_count+1
      show_render_data.append(
        {
          "start_time" : show.start_time,
          "venue_id" : show.venue_id,
          "venue_image_link" : show.venue.image_link,
          "venue_name" : show.venue.name
        }
      )
    return [shows_count, show_render_data]

  past_shows = shows(past_shows)
  upcoming_shows = shows(upcoming_shows)

  artist.past_shows_count = past_shows[0]
  artist.past_shows = past_shows[1]

  artist.upcoming_shows_count = upcoming_shows[0]
  artist.upcoming_shows = upcoming_shows[1]

  return render_template('pages/show_artist.html', artist=artist)



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm()
  
  if form.validate():
    artist = Artist( 
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'], 
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      genres=form.genres.data,
      image_link=request.form['image_link'],
      website=request.form['website']
      )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed')
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  all_shows = db.session.query(Show).join(Artist).join(Venue).all()
  for show in all_shows:
    data.append({
          "venue_id" : show.venue_id,
          "venue_name" : show.venue.name,
          "artist_id" : show.artist_id,
          "artist_image_link" : show.artist.image_link,
          "artist_name" : show.artist.name,
          "start_time" : show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if form.validate():

    artist_id=request.form['artist_id'],
    venue_id=request.form['venue_id'],
    start_time=request.form['start_time']
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    start_time = start_time

    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    artist.show =[new_show]
    venue.show =[new_show]
    db.session.add_all([artist,venue, new_show])
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Show could not be listed.')
    return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
