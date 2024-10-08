from flask import Blueprint, render_template, request, redirect, flash, g, session
from app import db
from app.models import Credentials, Customer, Company, Cruise, Destination, BookingRecord
from sqlalchemy import text
import random
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = Customer.query.get(session['user_id'])

@bp.route('/')
def home():
    home_msg = 'Welcome to CruiseWithMe'
    return render_template("home.html", homeMsg=home_msg)

@bp.route('/login')
def login():
    return render_template("login.html", promptMsg="Please login to your account")

@bp.route('/user_login', methods=['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']

    credentials = Credentials.query.filter_by(cust_username=username).first()

    if not credentials:
        return render_template("login.html", promptMsg="Your username doesn't exist in our database⚠️, please try again⚠️")

    if password == credentials.cust_password:
        customer = Customer.query.filter_by(cred_id=credentials.cred_id).first()
        session['user_id'] = customer.cust_id
        return render_template("user_home.html", userName=customer.cust_name)
    else:
        return render_template("login.html", promptMsg="Wrong password⚠️, please try again⚠️")

@bp.route('/register')
def register():
    return render_template("register.html", regMsg="Please register an account")

@bp.route('/user_register', methods=['POST'])
def user_register():
    username = request.form['username']
    password = request.form['password']
    budget = request.form['cust_budget']
    specialty = request.form['cust_specialty']
    rating = request.form['cust_rating']

    if Credentials.query.filter_by(cust_username=username).first():
        return render_template("register.html", regMsg="Username already exists⚠️, please choose another⚠️")

    new_cred_id = str(random.randint(0, 1000))
    while Credentials.query.get(new_cred_id):
        new_cred_id = str(random.randint(0, 1000))

    new_credentials = Credentials(cred_id=new_cred_id, cust_username=username, cust_password=password)
    db.session.add(new_credentials)

    new_cust_id = str(random.randint(0, 1000))
    while Customer.query.get(new_cust_id):
        new_cust_id = str(random.randint(0, 1000))

    new_customer = Customer(cust_id=new_cust_id, cred_id=new_cred_id, cust_name=username, 
                            cust_budget=budget, cust_specialty=specialty, cust_rating=rating)
    db.session.add(new_customer)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return render_template("register.html", regMsg="Registration failed⚠️, please try again⚠️")

    session['user_id'] = new_cust_id
    return render_template("user_home.html", userName=username)

@bp.route('/user_home')
def user_home():
    if not g.user:
        return redirect('/login')
    return render_template("user_home.html", userName=g.user.cust_name)

@bp.route('/find_company', methods=['POST'])
def find_company():
    if not g.user:
        return redirect('/login')

    company_id = request.form['compId']
    company = Company.query.get(company_id)

    if not company:
        return render_template("company_detail.html", userName=g.user.cust_name, 
                               promptMsg="Your Company doesn't exist in our database⚠️, please try again⚠️",
                               compInfo=None)

    return render_template("company_detail.html", userName=g.user.cust_name, 
                           promptMsg="Woohoo! We found your company 🍀",
                           compInfo=company)

@bp.route('/find_cruise', methods=['POST'])
def find_cruise():
    if not g.user:
        return redirect('/login')

    cruise_id = request.form['cruiseId']
    cruise = Cruise.query.get(cruise_id)

    if not cruise:
        return render_template("cruise_detail.html", userName=g.user.cust_name, 
                               promptMsg="Your cruise doesn't exist in our database⚠️, please try again⚠️",
                               destRecords=None)

    dest_records = cruise.sail_from + cruise.sail_to
    return render_template("cruise_detail.html", userName=g.user.cust_name, 
                           promptMsg="Woohoo! We found your cruise, and here's your destinations information🍀",
                           destRecords=dest_records)

@bp.route('/booking_records')
def booking_records():
    if not g.user:
        return redirect('/login')

    booking_records = BookingRecord.query.filter_by(cust_id=g.user.cust_id).all()
    cruise_records = [record.cruise for record in booking_records]
    cruise_records.sort(key=lambda x: x.cruise_start_date, reverse=True)

    return render_template("booking_records.html", userName=g.user.cust_name,
                           userRecords=booking_records, cruiseRecords=cruise_records)

@bp.route('/random_cruise')
def random_cruise():
    if not g.user:
        return redirect('/login')

    start_date = datetime.today().strftime('%Y-%m-%d')

    cruise = Cruise.query.join(Cruise.sail_to).join(Cruise.sail_from).filter(
        Cruise.cruise_cost <= g.user.cust_budget,
        Cruise.cruise_rating >= g.user.cust_rating,
        Cruise.cruise_start_date >= start_date,
        (Destination.dest_specialty == g.user.cust_specialty)
    ).order_by(db.func.random()).first()

    if not cruise:
        return render_template("random_cruise.html", userName=g.user.cust_name,
                               promptMsg="Oops, we didn't find a matching cruise for you :C",
                               cruiseRecord=None, destRecords=None)

    dest_records = cruise.sail_from + cruise.sail_to
    return render_template("random_cruise.html", userName=g.user.cust_name,
                           promptMsg="Woohoo! We found a cruise for you 🍀",
                           cruiseRecord=cruise, destRecords=dest_records)

@bp.route('/book_cruise', methods=['POST'])
def book_cruise():
    if not g.user:
        return redirect('/login')

    cruise_id = request.form['cruiseId']
    cruise = Cruise.query.get(cruise_id)

    if not cruise:
        return render_template("booking_results.html", userName=g.user.cust_name,
                               bookRecord=None,
                               promptMsg="⚠️ Oops, something went wrong ⚠️ The cruise doesn't exist.")

    new_book_id = str(random.randint(0, 10000000))
    while BookingRecord.query.get(new_book_id):
        new_book_id = str(random.randint(0, 10000000))

    new_booking = BookingRecord(book_id=new_book_id, comp_id=cruise.comp_id,
                                cust_id=g.user.cust_id, cruise_id=cruise_id)
    db.session.add(new_booking)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return render_template("booking_results.html", userName=g.user.cust_name,
                               bookRecord=None,
                               promptMsg="⚠️ Oops, something went wrong ⚠️ You may have booked for this cruise already, or some unknown error occurred...")

    if any(not dest.dest_is_domestic for dest in cruise.sail_to + cruise.sail_from):
        flash("🛃   The cruise you've booked may need your PASSPORT, please be prepared!   🛃")

    return render_template("booking_results.html", userName=g.user.cust_name,
                           bookRecord=new_booking,
                           promptMsg="🎉 Congratulations on your successful booking! 🎉")

@bp.route('/direct_book')
def direct_book():
    if not g.user:
        return redirect('/login')
    return render_template("direct_book.html", userName=g.user.cust_name)

@bp.route('/directly_book', methods=['POST'])
def directly_book():
    if not g.user:
        return redirect('/login')

    cust_start_date = request.form['cust_start_date']
    cust_budget_loc = request.form['cust_budget']
    cust_rating_loc = request.form['cust_rating']
    cust_specialty_loc = request.form['cust_specialty']
    cust_climate_loc = request.form['cust_climate']
    is_domestic_loc = request.form['is_domestic']

    query = Cruise.query.join(Cruise.sail_to).join(Cruise.sail_from).filter(
        Cruise.cruise_start_date >= cust_start_date
    )

    if cust_budget_loc:
        query = query.filter(Cruise.cruise_cost <= float(cust_budget_loc))
    if cust_rating_loc:
        query = query.filter(Cruise.cruise_rating >= float(cust_rating_loc))
    if cust_specialty_loc:
        query = query.filter((Destination.dest_specialty == cust_specialty_loc))
    if cust_climate_loc:
        query = query.filter((Destination.dest_climate == cust_climate_loc))
    if is_domestic_loc == "TRUE":
        query = query.filter(Destination.dest_is_domestic == True)

    cruise_records = query.all()

    if cruise_records:
        promptMsg = "Woohoo! We found the cruises that suit you! 🍀"
    else:
        promptMsg = "Ooops! Currently, we don't have anything that matches your preferences. 🧎"

    return render_template("direct_cruise.html", userName=g.user.cust_name,
                           promptMsg=promptMsg, cruiseRecords=cruise_records)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')