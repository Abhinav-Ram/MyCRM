from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
import os
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField
from wtforms.validators import InputRequired

base_dir = basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()


def connect_db(app, database):
    app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, database)
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return db

def generate_unique_id(table):
    model_str = '___'
    if(table == 'lead_entries'): 
        last_entry = LeadEntry.query.order_by(LeadEntry.enquiry_number.desc()).first()
        print(last_entry)
        model_str = 'PCTENQ'
    elif(table == 'project'):
        #last_entry = ProjectEntry.query.order_by(ProjectEntry.proj_id.desc()).first()
        model_str = 'PCTPRJ'
    # Query the last entry in the table
    
    if last_entry is not None:
        if(table == 'lead_entries'): 
            last_id = last_entry.enquiry_number
        elif(table == 'project'):
            #last_id = last_entry.proj_id
            pass
        # Extract the last ID, extract number part, increment by 1, and append to 'PCTENQ' 
        last_id_number = int(str(last_id).split(model_str)[-1])
        new_id_number = last_id_number + 1
        new_id = model_str + f'{new_id_number:06}'  # Assuming the number part has 6 digits
    else:
        # If no entries exist, start with PCTENQ000001
        new_id = model_str + '000001'

    return new_id

def generate_unique_quote_version(lead_id):
    # Query the last quote entry for the given lead_id
    last_quote = QuoteEntry.query.filter_by(quote_id=lead_id).order_by(QuoteEntry.quote_version.desc()).first()

    if last_quote is not None:
        last_version = last_quote.quote_version
        new_version = last_version + 1
    else:
        # If no entries exist, start with version 1
        new_version = 1

    return new_version


class Salesman(db.Model):
    __tablename__ = 'salesmen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"{self.id} - {self.name}"

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    address = db.Column(db.String(100), nullable=False, unique=False)
    vertical = db.Column(db.String(20), nullable=False, unique=False)
    gst_number = db.Column(db.String(20), unique=True) 
    db.UniqueConstraint(gst_number, name='unique_gst_number')

    def __repr__(self):
        return f"{self.id} - {self.name}"


class LeadEntry(db.Model):
    __tablename__ = 'lead_entries'
    enquiry_number = db.Column(db.String(50), primary_key=True, nullable=False)
    customer_details = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False) 
    product_details = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    sales_account_mgr_id = db.Column(db.Integer, db.ForeignKey('salesmen.id'), nullable=False)
    presales_support_id = db.Column(db.Integer, db.ForeignKey('salesmen.id'), nullable=False)
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)
    estimate_cost = db.Column(db.Float, nullable=True)
    closure_date = db.Column(db.Date)

    customer = db.relationship('Customer', foreign_keys=[customer_details])
    sales_account_mgr = db.relationship('Salesman', foreign_keys=[sales_account_mgr_id])
    presales_support = db.relationship('Salesman', foreign_keys=[presales_support_id])

    def __init__(self, enquiry_number, customer_details, product_details, product_description, 
                 sales_account_mgr_id, presales_support_id, remarks, status, estimate_cost, closure_date=None):
        self.enquiry_number = enquiry_number
        self.customer_details = customer_details
        self.product_details = product_details
        self.product_description = product_description
        self.sales_account_mgr_id = sales_account_mgr_id
        self.presales_support_id = presales_support_id
        self.remarks = remarks
        self.status = status
        self.estimate_cost = estimate_cost
        self.closure_date = closure_date

    def __repr__(self):
        return f"Lead {self.enquiry_number}"

def salesman_choices():      
    return [int(each.id) for each in db.session.query(Salesman).all()]

def customer_choices():      
    return [int(each.id) for each in db.session.query(Customer).all()]

def get_all_entries(table):
    entries = None
    if(table == 'lead_entries'): 
        entries = LeadEntry.query.all() 
    elif(table == 'project'):
        pass
        #entries = ProjectEntry.query.all()
    return entries
 
# Define the lead entry form class
class LeadEntryForm(FlaskForm):
    customer_details = SelectField('Customer Details', coerce=int, choices=customer_choices, validators=[InputRequired()])
    product_details = StringField('Product Details', validators=[InputRequired()])
    product_description = TextAreaField('Product Description', validators=[InputRequired()])
    sales_account_mgr = SelectField('Sales Account Manager', coerce=int, choices=salesman_choices, validators=[InputRequired()])
    presales_support = SelectField('Presales Support', coerce=int, choices=salesman_choices, validators=[InputRequired()])
    remarks = TextAreaField('Remarks')
    status = SelectField('Status', choices=[('FUNNEL', 'Funnel'), ('COMMIT', 'Commit'), ('ORDER_WON', 'Order Won'),
                                            ('ORDER_LOST', 'Order Lost'), ('QUOTE_NOT_SENT', 'Quote Not Sent')],
                         validators=[InputRequired()])
    estimate_cost = DecimalField('Estimate Cost', validators=[InputRequired()])
    closure_date = DateField('Tentative Closure Date', format='%Y-%m-%d', validators=[InputRequired()])

class QuoteEntry(db.Model):
    quote_version = db.Column(db.Integer, nullable=False, primary_key=False, unique=False)
    quote_id = db.Column(db.String, db.ForeignKey('lead_entries.enquiry_number'), primary_key=False, nullable=False, unique=False)
    items = db.Column(db.JSON, nullable=True)
    quote = db.relationship('LeadEntry', foreign_keys=[quote_id])

    __table_args__ = (
        db.PrimaryKeyConstraint('quote_version', 'quote_id'),
    )

    def __repr__(self):
        return f"Lead {self.quote_id}"
