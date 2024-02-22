import datetime
from flask import Flask, session, abort, redirect, request, render_template, flash, url_for, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import database
from database import connect_db
from flask_migrate import Migrate
import pandas as pd
import json

app = Flask(__name__)
company_data = None
db = connect_db(app, 'crm.db')
migrate = Migrate(app, db)

def create_app():
    with app.app_context():
        db.create_all()
        db.session.commit()
    return app

app = create_app()

app.secret_key = "@209AoRQeFkeW"


@app.route('/')
def home():
    return render_template('home.html', pagetitle='CRM Home')

@app.route('/leads/')
def leads():
    return render_template('leads.html', lead_entries = database.get_all_entries('lead_entries'), pagetitle='Lead Table')

@app.route('/leads/entry/', methods=['GET', 'POST'])
def lead_entry():
    form = database.LeadEntryForm()
    if form.validate_on_submit():
        # Create a new lead entry instance using form data
        lead_entry = database.LeadEntry(
            enquiry_number=database.generate_unique_id('lead_entries'),  # Implement this function to generate unique enquiry numbers
            customer_details=form.customer_details.data,
            product_details=form.product_details.data,
            product_description=form.product_description.data,
            sales_account_mgr_id=form.sales_account_mgr.data,
            presales_support_id=form.presales_support.data,
            remarks=form.remarks.data,
            status=form.status.data,
            estimate_cost=form.estimate_cost.data,
            closure_date=form.closure_date.data
        )
        #print(lead_entry.enquiry_number)
        # Save the lead entry to the database
        db.session.add(lead_entry)
        db.session.commit()

        # Redirect to a success page or another route
        return redirect('/leads/')

    return render_template('lead_entry.html', form=form, pagetitle='Lead Generator', cust = database.Customer, sales = database.Salesman)

@app.route('/leads/view/')
def lead_view():
    lead_id=request.args.get('lead_id')
    lead = database.LeadEntry.query.get_or_404(lead_id)
    quote_list = database.QuoteEntry.query.filter_by(quote_id=lead_id).order_by(database.QuoteEntry.quote_version.desc())
    if lead:
        return render_template('lead_view.html', lead=lead, quote_list=quote_list, today=datetime.date.today(), cdata=company_data)
    else:
        return "Lead not found"

@app.route('/leads/edit/', methods=['GET', 'POST'])
def lead_edit():
    lead_id = request.args.get('lead_id')
    lead = database.LeadEntry.query.get_or_404(lead_id)
    form = database.LeadEntryForm(obj=lead)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            lead.sales_account_mgr = database.Salesman.query.get_or_404(form.sales_account_mgr.data)
            lead.presales_support = database.Salesman.query.get_or_404(form.presales_support.data)
            lead.customer = database.Customer.query.get_or_404(form.customer_details.data)
            lead.product_details = form.product_details.data
            lead.product_description = form.product_description.data
            lead.remarks = form.remarks.data
            lead.status = form.status.data
            lead.estimate_cost = form.estimate_cost.data
            lead.closure_date = form.closure_date.data
            db.session.commit()
            flash('Lead updated successfully!', 'success')
            return redirect(url_for('lead_view', lead_id=lead.enquiry_number))
    elif request.method == 'GET':
        form.sales_account_mgr.data = lead.sales_account_mgr_id 
        form.presales_support.data = lead.presales_support_id 
        form.customer_details.data = lead.customer_details
        form.product_details.data = lead.product_details
        form.product_description.data = lead.product_description
        form.remarks.data = lead.remarks
        form.status.data = lead.status
        form.estimate_cost.data = lead.estimate_cost
        form.closure_date.data = lead.closure_date
    
    return render_template('lead_edit.html', form=form, lead_id=lead_id)

@app.route('/leads/download/', methods=['GET','POST'])
def download_leads():
    lead_entries = database.LeadEntry.query.all()
    customer_names = {customer.id: customer.name for customer in database.Customer.query.all()}
    sales_account_mgr_names = {salesman.id: salesman.name for salesman in database.Salesman.query.all()}
    presales_support_names = {salesman.id: salesman.name for salesman in database.Salesman.query.all()}
    df = pd.DataFrame([
        (lead.enquiry_number, customer_names.get(lead.customer_details), lead.product_details, lead.product_description, 
         sales_account_mgr_names.get(lead.sales_account_mgr_id), presales_support_names.get(lead.presales_support_id), 
         lead.remarks, lead.status, lead.estimate_cost, lead.closure_date) 
        for lead in lead_entries
    ], columns=['Enquiry Number', 'Customer Details', 'Product Details', 'Product Description', 
                'Sales Account Mgr', 'Presales Support', 'Remarks', 'Status', 'Estimate Cost', 'Closure Date'])
    excel_file_path = 'leads.xlsx'
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

@app.route('/leads/quotes/entry/', methods=['GET'])
def quote_entry():
    lead_id = request.args.get('lead_id')
    lead = database.LeadEntry.query.get_or_404(lead_id)
    last_number = database.generate_unique_quote_version(lead_id)

    if last_number == 1:
        # If no quotes exist for the lead, go to quote_entry.html to add a new quote
        return render_template('quote_entry.html', lead=lead, today=datetime.date.today(), gst=company_data["gstpercent"])
    else:
        existing_quote = database.QuoteEntry.query.filter_by(quote_id=lead_id, quote_version=last_number - 1).first()
        # Create a new quote object for revision (increment quote_version)
        new_quote = database.QuoteEntry(
            quote_id=lead_id,
            quote_version=last_number,
            items = existing_quote.items,
        )

        # Pass the new quote object to quote_revise.html along with lead, date, and company data
        return render_template('quote_revise.html', lead=lead, quote=new_quote, today=datetime.date.today(), gst=company_data["gstpercent"])

@app.route('/leads/quotes/entry_success/', methods=['GET','POST'])
def quote_entry_success():
    # Retrieve form data from hidden fields
    if request.method == 'GET':
        quote = database.QuoteEntry()
        lead_id = request.args.get('quotationNo')
        lead = database.LeadEntry.query.get_or_404(lead_id)
        quote.quote_id = lead_id
        quote.items = {}
        print(request.args.get('productNameAll').rstrip(',').split(','))
        quote.items['product_names'] = request.args.get('productNameAll').rstrip(',').split(',')
        quote.items['product_descriptions']=request.args.get('productDescriptionAll').rstrip(',').split(',')
        quote.items['quantities'] = request.args.get('quantityAll').rstrip(',').split(',')
        quote.items['uoms'] = request.args.get('uomAll').rstrip(',').split(',')
        quote.items['rates'] = request.args.get('rateAll').rstrip(',').split(',')
        quote.items['amounts'] = request.args.get('amountAll').rstrip(',').split(',')
        quote.items['margin_types'] = request.args.get('marginTypeAll').rstrip(',').split(',')
        quote.items['margin_amounts'] = request.args.get('marginAmountAll').rstrip(',').split(',')
        quote.items['total_amounts'] = request.args.get('totalAll').rstrip(',').split(',')
        
        quote_version = database.generate_unique_quote_version(lead_id)
        quote.quote_version = quote_version

        db.session.add(quote)
        db.session.commit()

        # Pass the data to the template
        return redirect(url_for('lead_view', lead_id=lead_id))
    else:
        return None

@app.route('/leads/quotes/view/')
def quote_view():
    quote_id = request.args.get('quote_id')
    print('kaka', quote_id)
    quote_version = request.args.get('quote_version')
    quote = database.QuoteEntry.query.filter_by(quote_id=quote_id, quote_version=quote_version).first()
    lead = database.LeadEntry.query.get_or_404(quote_id)
    type = request.args.get('type')
    print(type)
    if type == '1':
        return render_template('quote_view.html', quote=quote, lead=lead, today=datetime.date.today(), cdata=company_data)
    elif type == '2':
        return render_template('cquote_view.html', quote=quote, lead=lead, today=datetime.date.today(), cdata=company_data)
def main():
    global company_data
    with open('company.json', 'r') as f:
        company_data = json.load(f)
    app.run(host='127.0.0.1', port='5000', debug=True)

if __name__ == "__main__":
    main()
