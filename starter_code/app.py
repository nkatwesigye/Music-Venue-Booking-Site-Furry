#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from datetime import datetime
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String,unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show_venue = db.relationship('Shows',backref='Venue', lazy = True)
    seeking_talent = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    show = db.relationship('Shows',backref='Artist', lazy = True)


class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    aritist_id = db.Column(db.Integer,db.ForeignKey(Artist.id),nullable = False)
    venue_id = db.Column(db.Integer,db.ForeignKey(Venue.id),nullable = False)
    start_time = db.Column(db.DateTime)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  refined_list=[]
  venue_names = str()
  data=Venue.query.with_entities(Venue.city,Venue.name,Venue.id,Venue.state).order_by(Venue.city)
  sorted_venue_dict={}
  city_state_dict = {}
  venue_id_dict = {}

  for values in data :
      refined_list.append(values.city)
      venue_id_dict[values.name] = values.id
      if values.state:
         city_state_dict[values.city] = values.state
      for city in set(refined_list):
          if city in sorted_venue_dict.keys() and values.city == city:
            venue_name_list = sorted_venue_dict[city] + ', ' + (values.name)
            sorted_venue_dict[city] = venue_name_list
          elif city == values.city:
              sorted_venue_dict[city] = venue_names + (values.name)

  return render_template('pages/venues.html',city_state_dict=city_state_dict,\
  sorted_venue_dict=sorted_venue_dict,venue_id_dict=venue_id_dict,\
  refined_list=set(refined_list),areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  response = Venue.query.filter(Venue.name.ilike('%'+ search_term + '%'))
  return render_template('pages/search_venues.html', results=response, \
  search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  data = Venue.query.filter_by(id=venue_id).all()

  presentshows = Artist.query.with_entities(Artist.id,Artist.name \
  ,Artist.image_link,Shows.venue_id,Shows.start_time).join(Shows \
  ,(Shows.start_time >= datetime.now()) & (Artist.id == Shows.aritist_id) \
   & (Shows.venue_id == venue_id))

  pastshows = Artist.query.with_entities(Artist.id,Artist.name \
  ,Artist.image_link,Shows.start_time).join(Shows,
  (Shows.start_time <= datetime.now()) & (Artist.id == Shows.aritist_id) \
   & (Shows.venue_id == venue_id))


  return render_template('pages/show_venue.html', venues=data ,presentshows=presentshows\
    , pastshows=pastshows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    musictype = ''
    name = request.form.get('name','')
    city = request.form.get('city','')
    genres = request.form.getlist('genres')
    state  = request.form.get('state','')
    image_link = request.form.get('image_link','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    musictype = (',').join(genres)
    venue = Venue(name=name ,city=city , genres=musictype,state=state,\
    image_link=image_link,address=address,phone=phone,facebook_link=facebook_link)
    db.session.add(venue)
    try:
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      db.session.flush()
      flash('An error occurred. Venue ' + name + ' could not be listed.')
      return ( name + " " +  " was not created")


  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods= ['GET','DELETE'])
def delete_venue(venue_id):

    deleted_venue_name = request.get_json()['venue_to_delete_name']
    data = Venue.query.filter_by(id=venue_id).delete()
    try:
      db.session.commit()
      flash('Delete successful. Venue ' + deleted_venue_name + ' has been deleted')
      return redirect(url_for('venues'))
    except Exception as e:
      db.session.rollback()
      db.session.flush() # for resetting non-commited .add()
      flash('An error occurred. Venue ' + deleted_venue_name + ' was not deleted')
      return redirect(url_for('venues'))

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    #return (render_template('pages/home.html'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=Artist.query.with_entities(Artist.id,Artist.name)
  #
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term=request.form.get('search_term', '')
    response =Artist.query.filter(Artist.name.ilike('%'+ search_term + '%'))
    return render_template('pages/search_venues.html', results=response, \
    search_term=request.form.get('search_term', ''))

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # return render_template('pages/search_artists.html', results=response, \
  # search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_data = Artist.query.filter_by(id=artist_id).all()

    artist_presentshows = Artist.query.with_entities(Artist.id,Artist.name \
    ,Artist.image_link,Shows.aritist_id,Shows.start_time).join(Shows \
    ,(Shows.start_time >= datetime.now()) & (Artist.id == Shows.aritist_id) \
     & (Shows.aritist_id == artist_id))

    artist_pastshows = Artist.query.with_entities(Artist.id,Artist.name \
    ,Artist.image_link,Shows.start_time).join(Shows,
    (Shows.start_time <= datetime.now()) & (Artist.id == Shows.aritist_id) \
     & (Shows.aritist_id == artist_id))

    return render_template('pages/show_artist.html', artists=artist_data\
    ,presentshows=artist_presentshows, pastshows=artist_pastshows)
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = Artist.query.filter_by(id=artist_id).all()
  return render_template('forms/edit_artist.html',form=form, artists=artist_data)
  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    musictype = ''
    name = request.form.get('name','')
    city = request.form.get('city','')
    genres = request.form.getlist('genres')
    state  = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    musictype = (',').join(genres)
    try:
        data = Artist.query.filter_by(id=artist_id).first()
        data.name = name
        data.city = city
        data.genres = musictype
        data.state = state
        data.address = address
        data.phone = phone
        data.facebook_link = facebook_link
        db.session.commit()
        return redirect(url_for('show_artist',artist_id=artist_id ))
    except:
        db.session.rollback()
        return redirect(url_for('index'))
    finally:
        db.session.close()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue_data = Venue.query.filter_by(id=venue_id).all()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venues=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    musictype = ''
    name = request.form.get('name','')
    city = request.form.get('city','')
    genres = request.form.getlist('genres')
    print ("Selected genres:", genres)
    state  = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    musictype = ','.join(genres)


    try:
        data = Venue.query.filter_by(id=venue_id).first()
        data.name = name
        data.city = city
        data.genres = musictype
        data.state = state
        data.address = address
        data.phone = phone
        data.facebook_link = facebook_link
        db.session.commit()
        return redirect(url_for('show_venue',genres=genres,venue_id=venue_id))
    except:
         db.session.rollback()
    finally:
         db.session.close()

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    name = request.form.get('name','')
    city = request.form.get('city','')
    genres = request.form.get('genres','')
    state  = request.form.get('state','')
    phone = request.form.get('phone','')
    facebook_link = request.form.get('facebook_link','')
    artist = Artist(name=name ,city=city , genres=genres,state=state,\
    phone=phone,facebook_link=facebook_link)
    db.session.add(artist)
    try:
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      db.session.flush()
      flash('An error occurred. Venue ' + name + ' could not be listed.')
      return ( name + " " +  " was not created")

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Artist.query.with_entities(Artist.id.label("artist_id"),Artist.image_link,\
  Artist.name.label("artist_name"),Shows.venue_id,Shows.name.label("venue_name"),Shows.start_time)\
  .join(Shows,(Artist.id == Shows.aritist_id))

  show_id = db.session.query(Venue,Shows).with_entities(Venue.id,Venue.name).\
  filter(Venue.id == Shows.venue_id).all()

  # # TODO: replace with real venues data.
  # # num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/shows.html', shows=data , show_id=show_id)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    artist_id =  request.form.get('artist_id','')
    venue_id =   request.form.get('venue_id','')
    start_time = request.form.get('start_time','')
    shows = Shows(aritist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(shows)
    try:
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      db.session.flush()
      flash('An error occurred. Show could not be listed.')
      return render_template('pages/home.html')

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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
