
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response

### New Imports 
import random
import traceback

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
# tried to use flash but doesn't seem to work well...
app.secret_key = b'whatever'

#Global Variables
cust_username = None
cred_id = None
cust_id = None
user_budget = None
user_specialty = None
user_rating = None

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://yn2443:7282@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

### Project Codes ###

@app.route('/')
def home():
  # reset global fields everytime return to home
  global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
  cust_username = None
  cred_id = None
  cust_id = None
  user_budget = None
  user_specialty = None
  user_rating = None 
  home_msg = 'Welcome to CruiseWithMe'
  context=dict(homeMsg = home_msg)
  return render_template("home.html", **context)

@app.route('/login')
def login():
  context = dict(promptMsg = "Please login to your account")
  return render_template("login.html", **context )

@app.route('/user_login', methods=['POST'])
def user_login():
  try:
    username = request.form['username']
    password = request.form['password']

    cursor = g.conn.execute('SELECT C.cred_id, C.cust_password FROM credentials C WHERE C.cust_username= (%s)', username)
    # case 2.1 - unsuccessful login, non-existent user -> return to the login page
    if(cursor.rowcount <= 0):
      context = dict(promptMsg = "Your username doesn't exist in our database⚠️, please try again⚠️")
      return render_template("login.html", **context )
    # tested!

    result = cursor.fetchone()
    # case 1 - successful login -> move to user_home
    # tested :)
    
    if(password == result['cust_password']):
      # set global fields
      global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
      cust_username = username

      # fetch other user data needed
      cursor = g.conn.execute('SELECT * FROM customers_cred C WHERE C.cust_name = (%s)', cust_username)
      result = cursor.fetchone()
      # #debug
      # print(result)
      cred_id = result['cred_id']
      cust_id = result['cust_id']
      user_budget = result['cust_budget']
      user_specialty = result['cust_specialty']
      user_rating = result['cust_rating']
      # tested :)

      context = dict(userName = cust_username)
      print((cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating))
      return render_template("user_home.html", **context)
    # case 2.2 - unsuccessful login -> return to the login page
    # tested!
    else:
      context = dict(promptMsg = "Wrong password⚠️, please try again⚠️")
      return render_template("login.html", **context )
  except:
    context = dict(promptMsg = "Error during login⚠️, please verify and try again⚠️")
    return render_template("login.html", **context )
  

@app.route('/register')
def register():
  context = dict(regMsg = "Please register an account")
  return render_template("register.html", **context)

@app.route('/user_register', methods=['POST'])
def user_register():
  
  # #debug
  # print(request.form)
  username = request.form['username']
  password = request.form['password']
  budget = request.form['cust_budget']
  specialty = request.form['cust_specialty']
  rating = request.form['cust_rating']
 
  # randomly assign cred_id
  cursor = g.conn.execute('SELECT cred_id FROM credentials')
  new_cred_id =  random.randint(0,1000)

  results = cursor.fetchall()

  while( new_cred_id in results):
    new_cred_id = random.randint(0,1000)
  
  # case 2.1 - failed registration, failed insertion into credentials
  try:
    # step 1 - insert cust_username cust_password
    args = (str(new_cred_id), username, password)
    g.conn.execute('INSERT INTO credentials(cred_id, cust_username, cust_password) VALUES(%s, %s, %s)', args)
  except:
    traceback.print_exc()
    context = dict(regMsg = "Invalid username ⚠️, please try again⚠️")
    return render_template("register.html", **context)
  
  # randomly assign cust_id
  cursor = g.conn.execute('SELECT cust_id FROM customers_cred')
  new_cust_id =  random.randint(0,1000)

  results = cursor.fetchall()

  while( new_cust_id in results):
    new_cust_id = random.randint(0,1000)
  
  try:
    args = (str(new_cust_id), str(new_cred_id), username, budget, specialty, rating)
    g.conn.execute('INSERT INTO customers_cred(cust_id, cred_id, cust_name, cust_budget, cust_specialty, cust_rating) VALUES(%s, %s, %s, %s, %s, %s)', args)
  except:
    traceback.print_exc()
    g.conn.execute('DELETE FROM credentials C WHERE C.cust_username=(%s)', username)
    # case 2.2 - failed registration, failed insertion into customers_cred
    context = dict(regMsg = "Invalid preferences ⚠️, please try again⚠️")
    return render_template("register.html", **context)

  # case 1 - successful registration, continue to user_home
  # set global fields
  global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
  cust_username = username
  cred_id = str(new_cred_id)
  cust_id = str(new_cust_id)
  user_budget = budget
  user_specialty = specialty
  user_rating = rating

  context = dict(userName = cust_username)
  print((cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating))
  return render_template("user_home.html", **context)
 
@app.route('/user_home')
def user_home():
  # only way to use this direct url is after login/register
  # either way, globals must have been set
  global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
  context=dict(userName = cust_username)

  return render_template("user_home.html", **context)


@app.route('/find_company', methods=['POST'])
def find_company():
  company_id = request.form['compId']
  context = dict(compId = company_id)
  #
  return render_template("company_detail.html", **context)

@app.route('/find_cruise', methods=['POST'])
def find_cruise():
  cruise_id = request.form['cruiseId']
  context = dict(cruiseId = cruise_id)
  return render_template("company_detail.html", **context)


@app.route('/home')
def home_2():
  home_msg = 'Welcome Back to CruiseWithMe'
  context=dict(homeMsg = home_msg)
  return render_template("home.html", **context)



@app.route('/booking_records')
def booking_recrods():
  # everytime get to booking_records, use globals to fetch info needed.
  global cust_username, cred_id, cust_id
  try:
    booking_records = {}
    cruise_records = []

    cursor = g.conn.execute('SELECT * FROM booking_records b WHERE b.cust_id = (%s)', cust_id)
    booking_records = cursor.fetchall()
    for record in booking_records:
      cruise_id = record['cruise_id']
      # get cruise_info
      cursor = g.conn.execute('SELECT * FROM cruises c WHERE c.cruise_id = (%s)', cruise_id)
      cruise = cursor.fetchone()
      cruise_records.append(cruise)
    
    context=dict(userName = cust_username)
    # booking_records
    context.update(userRecords = booking_records)
    # cruise
    context.update(cruiseRecords = cruise_records)
  except:
    traceback.print_exc()
    context = dict(userName = cust_username)
    return render_template("user_home.html", **context)

  return render_template("booking_records.html", **context)



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
