from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail


# Initialize app
app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 
app.config['MAIL_PASSWORD'] = 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# Environment
ENV = 'prod'

# Development
if ENV == 'env':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devfruit.db'
    app.debug = True
    # When in development postgresql database is used
    
else:
    # Production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devfruit.db'
    app.debug = False
    

# added to stop warning message
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database object
db = SQLAlchemy(app)

class Feedback(db.Model):
    __tablename__='feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    # Initializer/constructor
    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

    """
    python command used to look at model, database and creates feedback table
    python
    from app import db
    db.create_all()
    """

# Main/default page loaded (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Submit page rendered when submit action post is called by form
@app.route('/submit', methods=['POST'])
def submit():
    # Checks that the submit is a POST method and not a GET
    if request.method == 'POST':
        # Gets information from the form variables
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        # print(customer, dealer, rating, comments)
        
        # Checks if customer and dealer are empty
        if customer == '' or dealer == '':
            # if fields are empty, index/html is rendered and message is output to user
            return render_template('index.html', message='Please enter required fields')
        
        # Checks if customer doesnt already exist
        # Commits feedback to db, renders success page after form submission
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()

            # Connect and send email
            send_mail(customer,dealer, rating, comments)

            # Render success.html page
            return render_template('success.html')
        
        # If customer is duplicated, index rendered and message output to user
        return render_template('/index.html', message='You have already submitted feedback')


if __name__ == '__main__':
    app.run()