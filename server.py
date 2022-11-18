
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
from sqlalchemy import sql
from datetime import datetime



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


# #
# # @app.route is a decorator around index() that means:
# #   run index() whenever the user tries to access the "/" path using a GET request
# #
# # If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
# #
# #       @app.route("/foobar/", methods=["POST", "GET"])
# #
# # PROTIP: (the trailing / in the path is important)
# #
# # see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# # see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
# #
# @app.route('/index')
# def index():
#   """
#   request is a special object that Flask provides to access web request information:

#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

#   See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

#   """

#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args)

#   #
#   # example of a database query
#   #
#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

#   #
#   # Flask uses Jinja templates, which is an extension to HTML where you can
#   # pass data to a template and dynamically generate HTML based on the data
#   # (you can think of it as simple PHP)
#   # documentation: https://realpython.com/primer-on-jinja-templating/
#   #
#   # You can see an example template in templates/index.html
#   #
#   # context are the variables that are passed to the template.
#   # for example, "data" key in the context variable defined below will be
#   # accessible as a variable in index.html:
#   #
#   #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#   #     <div>{{data}}</div>
#   #
#   #     # creates a <div> tag for each element in data
#   #     # will print:
#   #     #
#   #     #   <div>grace hopper</div>
#   #     #   <div>alan turing</div>
#   #     #   <div>ada lovelace</div>
#   #     #
#   #     {% for n in data %}
#   #     <div>{{n}}</div>
#   #     {% endfor %}
#   #
#   context = dict(data = names)

#   #
#   # render_template looks in the templates/ folder for files.
#   # for example, the below file reads template/index.html
#   #
#   return render_template("index.html", **context)

# #
# # This is an example of a different path.  You can see it at:
# #
# #     localhost:8111/another
# #
# # Notice that the function name is another() rather than index()
# # The functions for each app.route need to have different names
# #
# @app.route('/another')
# def another():
#   return render_template("another.html")

# # Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')

### Project Codes ###


@app.route('/')
def home_2():
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
      # print((cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating))
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

  #flatten and convert to int()
  results = cursor.fetchall()
  results = [int(item) for items in results for item in items]

  while( new_cred_id in results):
    new_cred_id = random.randint(0,1000)
  
  # case 2.1 - failed registration, failed insertion into credentials
  try:
    # step 1 - insert cust_username cust_password
    args = (str(new_cred_id), username, password)
    g.conn.execute('INSERT INTO credentials(cred_id, cust_username, cust_password) VALUES(%s, %s, %s)', args)
  except:
    traceback.print_exc()
    context = dict(regMsg = "Invalid username or password ⚠️, please try again⚠️")
    return render_template("register.html", **context)
  
  # randomly assign cust_id
  cursor = g.conn.execute('SELECT cust_id FROM customers_cred')
  new_cust_id =  random.randint(0,1000)

  #flatten and convert to int()
  results = cursor.fetchall()
  results = [int(item) for items in results for item in items]

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
  # print((cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating))
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
  global cust_username
  
  company_id = request.form['compId']
  context = dict(compId = company_id)
  context.update(userName = cust_username)

  # fetch company
  cursor = g.conn.execute('SELECT * FROM companies C WHERE C.comp_id= (%s)', company_id)

  # case 1 - DNE
  if(cursor.rowcount <= 0):
    context.update(promptMsg = "Your Company doesn't exist in our database⚠️, please try again⚠️")
    context.update(compInfo = None)
    return render_template("company_detail.html", **context )

  # both cases tested!

  # case 2 - normal
  result = cursor.fetchone()
  context.update(compInfo = result)
  context.update(promptMsg = "Woohoo! We found your company 🍀")
  return render_template("company_detail.html", **context)

@app.route('/find_cruise', methods=['POST'])
def find_cruise():
  global cust_username

  cruise_id = request.form['cruiseId']
  context = dict(cruiseId = cruise_id)
  context.update(userName = cust_username)
  dest_records = []

  # fetch cruise
  cursor = g.conn.execute('SELECT * FROM cruises c WHERE c.cruise_id = (%s)', cruise_id)
  
  # case 1 - DNE
  if(cursor.rowcount <= 0):
    context.update(promptMsg = "Your cruise doesn't exist in our database⚠️, please try again⚠️")
    context.update(destRecords = None)
    return render_template("cruise_detail.html", **context)

  # case 2 - normal
  context.update(promptMsg = "Woohoo! We found your cruise, and here's your destinations information🍀")
  sail_to = None
  sail_from = None
  cursor = g.conn.execute('SELECT dest_id FROM sail_to s WHERE s.cruise_id = (%s)', cruise_id)
  sail_to = cursor.fetchone()['dest_id']
  cursor = g.conn.execute('SELECT dest_id FROM sail_from s WHERE s.cruise_id = (%s)', cruise_id)
  sail_from = cursor.fetchone()['dest_id']

  cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',sail_from)
  dest_record = cursor.fetchone()
  dest_records.append(dest_record)
  if(sail_to != sail_from):
    cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',sail_to)
    dest_record = cursor.fetchone()
    dest_records.append(dest_record)

  context.update(destRecords = dest_records)
  return render_template("cruise_detail.html", **context)


@app.route('/home')
def home():
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
    context=dict(userName = cust_username)

    cursor = g.conn.execute('SELECT * FROM booking_records b WHERE b.cust_id = (%s)', cust_id)
    #case 1 - DNE
    if(cursor.rowcount <= 0):
      context.update(userRecords = None)
      context.update(cruiseRecords = None)
      return render_template("booking_records.html", **context)

    #case 2 - normal
    booking_records = cursor.fetchall()
    for record in booking_records:
      print(record['cruise_id'])
      cruise_id = record['cruise_id']
      type(cruise_id)
      # get cruise_info
      cursor = g.conn.execute('SELECT * FROM cruises c WHERE c.cruise_id = (%s)', str(cruise_id))
      if(cursor.rowcount != 0):
        cruise = cursor.fetchone()
        cruise_records.append(cruise)
    #both tested!
    
    # booking_records
    context.update(userRecords = booking_records)
    # cruise
    print(cruise_records)
    cruise_records.sort(key=lambda x: x['cruise_start_date'], reverse=True)
    context.update(cruiseRecords = cruise_records)
  except:
    traceback.print_exc()
    context = dict(userName = cust_username)
    return render_template("user_home.html", **context)

  return render_template("booking_records.html", **context)

# @app.route('/filtered_cruise')
# def filtered_cruise():
#   global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
#   context = dict(userName = cust_username)
#   try:
#     cursor = g.conn.execute("SELECT * FROM cruises c, destinations d WHERE c.cruise_cost <= '{}' AND c.cruise_rating >= '{}' AND d.dest_specialty = '{}'".format(user_budget, user_rating, user_specialty))
#     # case 1 = DNE
#     if (cursor.rowcount <= 0):
#       context.update(promptMsg = "Oops, we didn't find a matching cruise for you :C")
#       return render_template("filtered_cruise.html", **context)
#     # case 2 = normal
#     valid_cruises = cursor.fetchall()
#     context.update(valid_cruises = valid_cruises)
#     context.update(promptMsg = "Here are cruises that match your preferences 😏")
#     return render_template("filtered_cruise.html", **context)
#   except:
#     traceback.print_exc()
#     context = dict(userName = cust_username)
#     return render_template("user_home.html", **context)

@app.route('/random_cruise')
def random_cruise():
  global cust_username, cred_id, cust_id, user_budget, user_specialty, user_rating
  context = dict(userName = cust_username)
  tpl = None
  dest_records = []

  start_date = datetime.today().strftime('%Y-%m-%d')
  print(start_date)

  try:
    # satisfying all the conditions, i.e. user_budget, user_specialty, user_rating
    cursor = g.conn.execute('SELECT s1.cruise_id, s1.dest_id AS to_dest, s2.dest_id AS from_dest FROM cruises c, sail_to s1, sail_from s2, destinations d1, destinations d2 WHERE c.cruise_id = s1.cruise_id AND s1.cruise_id = s2.cruise_id AND s1.dest_id = d1.dest_id AND s2.dest_id = d2.dest_id AND c.cruise_cost <= (%s) AND c.cruise_rating >= (%s) AND c.cruise_start_date >=  (%s) AND (d1.dest_specialty = (%s) OR d2.dest_specialty = (%s)) ORDER BY random() LIMIT 1',user_budget, user_rating, start_date, user_specialty, user_specialty)
    ## fully tested
    if(cursor.rowcount > 0):
      tpl = cursor.fetchone()

    # case 1 - DNE
    if (tpl == None):
      context.update(promptMsg = "Oops, we didn't find a matching cruise for you :C")
      context.update(cruiseRecord = None)
      context.update(destRecords = None)
      return render_template("random_cruise.html", **context)

    # case 2 - normal
    #
    # step 1 - fetch cruise
    cursor = g.conn.execute('SELECT * FROM cruises c WHERE c.cruise_id = (%s)', tpl['cruise_id'])
    cruise_record = cursor.fetchone()
    context.update(cruiseRecord = cruise_record) 

    # step 2 - fetch dest_records
    # reused from find_cruise()
    cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',tpl['from_dest'])
    dest_record = cursor.fetchone()
    dest_records.append(dest_record)
    if(tpl['from_dest'] != tpl['to_dest']):
      cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',tpl['to_dest'])
      dest_record = cursor.fetchone()
      dest_records.append(dest_record)

    # print(cruise_record)
    context.update(destRecords = dest_records)
    context.update(promptMsg = "Woohoo! We found your company 🍀")
    return render_template("random_cruise.html", **context)
  except:
    traceback.print_exc()
    context.update(promptMsg = "Something went wrong! Please go back to your options :C")
    return render_template("random_cruise.html", **context)

@app.route('/book_cruise', methods=['POST'])
def book_cruise():
  global cust_username, cust_id
  context=dict(userName = cust_username)
  cruise_id = request.form['cruiseId']
  
  try:
    # case 1 - success
    cursor = g.conn.execute('SELECT * FROM cruises c WHERE c.cruise_id = (%s)', cruise_id)
    comp_id = cursor.fetchone()['comp_id']

    # randomly assign book_id
    cursor = g.conn.execute('SELECT book_id FROM booking_records')
    new_book_id =  random.randint(0,10000)

    #flatten and convert to int()
    results = cursor.fetchall()
    results = [int(item) for items in results for item in items]

    while( new_book_id in results):
      new_book_id = random.randint(0,10000000)

    args = (str(new_book_id), comp_id, cust_id, cruise_id)
    g.conn.execute('INSERT INTO booking_records(book_id, comp_id, cust_id, cruise_id) VALUES(%s, %s, %s, %s)', args)

    cursor = g.conn.execute('SELECT * FROM booking_records b WHERE b.book_id = (%s)', str(new_book_id))

    booking_record = cursor.fetchone()

    # determine if the cruise is oversea and pop message if needed passport
    sail_to = None
    sail_from = None
    cursor = g.conn.execute('SELECT dest_id FROM sail_to s WHERE s.cruise_id = (%s)', cruise_id)
    sail_to = cursor.fetchone()['dest_id']
    cursor = g.conn.execute('SELECT dest_id FROM sail_from s WHERE s.cruise_id = (%s)', cruise_id)
    sail_from = cursor.fetchone()['dest_id']

    cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',sail_to)
    sail_to_dest_record = cursor.fetchone()
    cursor = g.conn.execute('SELECT * FROM destinations d WHERE d.dest_id = (%s)',sail_from)
    sail_from_dest_record = cursor.fetchone()

    if (sail_to_dest_record['dest_is_domestic'] == False) or (sail_from_dest_record['dest_is_domestic'] == False):
      # print("falsh prepared")
      flash("🛃   The cruise you've booked may need your PASSPORT, please be prepared!   🛃")

    context.update(bookRecord = booking_record)
    context.update(promptMsg = "🎉 Congratulations on your successful booking! 🎉")
    return render_template("booking_results.html", **context)
  
  except:
    # case 2 - failed
    traceback.print_exc()
    context.update(bookRecord = None)
    context.update(promptMsg = "⚠️ Oops, something went wrong ⚠️ You may have booked for this cruise already, or some unkown error occurs... ")
    return render_template("booking_results.html", **context)

@app.route('/direct_book')
def direct_book():
  # this is just a vanilla template just like any others;
  global cust_username
  context = None
  context = dict(userName = cust_username)
  return render_template("direct_book.html", **context)
  

@app.route('/directly_book', methods=['POST'])
def directly_book():
  global cust_username
  cruise_records = []
  context = None
  context = dict(userName = cust_username)

  # one last shot:
  
  # DESIGN CHANGE: still optional fields, using sql text;
  cust_budget_loc = request.form['cust_budget']
  cust_rating_loc = request.form['cust_rating']
  cust_specialty_loc = request.form['cust_specialty']
  cust_climate_loc = request.form['cust_climate']
  is_domestic_loc = request.form['is_domestic']

  #SELECT s1.cruise_id, s1.dest_id AS to_dest, s2.dest_id AS from_dest
  # reference: https://www.programcreek.com/python/example/51986/sqlalchemy.sql.text
  params = {}
  text = "SELECT * FROM cruises c, sail_to s1, sail_from s2, destinations d1, destinations d2 WHERE c.cruise_id = s1.cruise_id AND s1.cruise_id = s2.cruise_id AND s1.dest_id = d1.dest_id AND s2.dest_id = d2.dest_id "

  if cust_budget_loc != "":
    text += " AND c.cruise_cost <= :cruise_cost "
    params['cruise_cost'] = cust_budget_loc

  if cust_rating_loc != "":
    text += " AND c.cruise_rating >= :cruise_rating "
    params['cruise_rating'] = cust_rating_loc

  if cust_specialty_loc != "":
    text += " AND (d1.dest_specialty = :cust_specialty OR d2.dest_specialty = :cust_specialty ) "
    params['cust_specialty'] = cust_specialty_loc

  if cust_climate_loc != "":
    text += " AND (d1.dest_climate = :cust_climate OR d2.dest_climate = :cust_climate ) "
    params['cust_climate'] = cust_climate_loc

  if is_domestic_loc != "" and is_domestic_loc == "TRUE":
    text += " AND (d1.dest_is_domestic = :is_domestic AND d2.dest_is_domestic = :is_domestic ) "
    params['is_domestic'] = is_domestic_loc
  
  try:  
    cursor = g.conn.execute(sql.text(text), **params)
    for result in cursor:
      cruise_records.append(result)
  except:
    traceback.print_exc()
    context.update(promptMsg = "⚠️ Oops, something went wrong :C You may want to try again... ⚠️")
    return render_template("direct_cruise.html", **context)
  
  if len(cruise_records) > 0:
    context.update(promptMsg = "Woohoo! We found the cruises that suit you! 🍀")
    context.update(cruiseRecords = cruise_records)
  else:
    context.update(promptMsg = "Ooops! Currently, we don't have anything that matches your preferences. 🧎")
    context.update(cruiseRecords = None)

  return render_template("direct_cruise.html", **context)

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


