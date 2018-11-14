"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import User, Rating, Movie, connect_to_db, db
import operator


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


@app.route('/')
def index():
    """Homepage."""

    if session.get('user'):
    	return render_template("homepage.html")
    else:
    	return redirect("/login")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("users.html", users=users)

@app.route("/user_detail/<user>")
def user_detail(user):
    """Show list of users."""

    print(user)

    user = User.query.filter_by(user_id=user).one()

    print(user)

    return render_template("user_detail.html", user=user)


@app.route("/movies")
def movie_list():
    """Show list of users."""

    movies = Movie.query.all()
    movies = sorted(movies, key=operator.attrgetter('title'))
    # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects

    return render_template("movies.html", movies=movies)


@app.route("/movie_detail/<movie>")
def movie_detail(movie):
    """Show list of users."""
    print(movie)
    movie = Movie.query.filter_by(movie_id=movie).options(db.joinedload('ratings')).first()
    released_at= movie.released_at
    released_at=released_at.strftime('%b %d, %Y')
    # print(movie.ratings)
    # for movie in movie.ratings:
    # 	print(ratings.score)


    return render_template("movie_detail.html", movie=movie, ratings=movie.ratings, released_at=released_at)   

@app.route("/register", methods=['GET'])
def get_registration_form():

	if session['user']:
		print("user exists and is register")
		return redirect('/')
	else:
		return render_template("registration.html")


@app.route("/register", methods=['POST'])
def registration_process():
	
	email = request.form.get('email')
	password = request.form.get('password')

	users = User.query.filter_by(email = email).all()

	if users == []:
		user = User(email=email, password=password)
		db.session.add(user)
		db.session.commit()

	return redirect('/')

@app.route("/login", methods=['GET'])
def get_login_form():
	if session.get('user'):		
		return redirect("/")


	return render_template("login.html")

@app.route("/logged-in", methods=['GET'])
def log_user_in():
	email = request.args.get('email')
	password = request.args.get('password')

	print(email)
	print(password)

	user = User.query.filter_by(email = email).first()

	print(user)
	print(user.user_id)

	if user:
		print("something exists")
		if password == user.password:
			session['user'] = user.email
			flash("Logged in")
			return render_template("user_detail.html",
									user=user)
		else:
			print("Invalid password")
			flash("Invalid password")
			return redirect("/login")
	else:
		print("doesn't exist")
		return redirect("/register")

	return redirect("/login")

@app.route('/logout')
def logout():
	session.clear()
	flash("Logged out")
	return redirect('login')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
