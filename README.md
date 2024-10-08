# Cruise Booking Web Application

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.2.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-latest-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0.7-red.svg)

## Project Overview

This Cruise Booking Web Application is a comprehensive system designed to facilitate the process of browsing, selecting, and booking cruise trips. Developed as part of the Introduction to Databases course at Columbia University, this project showcases database management skills, web development proficiency, and software engineering practices.

## Key Features

1. **User Authentication**: Custom implementation of user registration and login functionality.
2. **Cruise Search**: Functionality allowing users to find cruises based on various criteria.
3. **Company and Cruise Details**: Detailed views for cruise companies and individual cruise offerings.
4. **Booking Management**: System for users to book cruises and view their booking history.
5. **Personalized Recommendations**: Basic algorithm to suggest random cruises based on user preferences.

## Technology Stack

- **Backend**: Python 3.x, Flask 2.2.3
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.7, Flask-SQLAlchemy 3.0.3
- **Frontend**: HTML, Jinja2 templates
- **Deployment**: The application is designed to be run locally, but could be adapted for production deployment

## Database Schema

The application uses a relational database with the following main tables:

1. **credentials**
   - cred_id (PK)
   - cust_username
   - cust_password

2. **customers_cred**
   - cust_id (PK)
   - cred_id (FK to credentials)
   - cust_name
   - cust_budget
   - cust_specialty
   - cust_rating

3. **companies**
   - comp_id (PK)
   - comp_name
   - comp_rating

4. **cruises**
   - cruise_id (PK)
   - comp_id (FK to companies)
   - cruise_name
   - cruise_cost
   - cruise_capacity
   - cruise_start_date
   - cruise_end_date
   - cruise_rating

5. **destinations**
   - dest_id (PK)
   - dest_name
   - dest_country
   - dest_climate
   - dest_specialty
   - dest_is_domestic

6. **sail_to** (Association table)
   - cruise_id (FK to cruises)
   - dest_id (FK to destinations)

7. **sail_from** (Association table)
   - cruise_id (FK to cruises)
   - dest_id (FK to destinations)

8. **booking_records**
   - book_id (PK)
   - comp_id (FK to companies)
   - cust_id (FK to customers_cred)
   - cruise_id (FK to cruises)

This schema demonstrates database design concepts including:
- Use of primary and foreign keys
- Many-to-many relationships (cruises to destinations)
- Data normalization to minimize redundancy

## Project Structure

```
cruise_booking_app/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── user_home.html
│       ├── company_detail.html
│       ├── cruise_detail.html
│       ├── booking_records.html
│       ├── random_cruise.html
│       ├── booking_results.html
│       ├── direct_book.html
│       └── direct_cruise.html
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

This structure follows a basic Flask application pattern, promoting modularity and scalability.

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cruise-booking-app.git
   cd cruise-booking-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database and update `config.py` with your database URI.

5. Run the application:
   ```
   python run.py
   ```

6. Access the application at `http://localhost:8111`

## Usage

1. Register a new account or log in with existing credentials.
2. Browse available cruises or use the search functionality to find specific options.
3. View detailed information about cruises and cruise companies.
4. Book a cruise and manage your bookings through the user dashboard.
5. Receive basic cruise recommendations based on your preferences.

## Future Enhancements

- Implement Flask-Login for more robust user authentication
- Utilize Flask-WTF for better form handling and CSRF protection
- Integrate Flask-Migrate for easier database schema management
- Enhance the frontend with CSS frameworks and JavaScript for a more interactive user experience
- Set up Gunicorn and a production-grade web server for deployment
- Implement real-time availability checking and booking
- Add a review and rating system for users to rate their cruise experiences
- Integrate a payment gateway for online payments
- Develop an admin interface for managing application data
- Implement data analytics for business intelligence


## Acknowledgments

- Professor Luis Gravano and the TAs of the Introduction to Databases course at Columbia University for their guidance and support.
- http://www.cs.columbia.edu/~gravano/cs4111/
