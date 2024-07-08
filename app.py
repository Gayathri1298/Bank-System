from flask import Flask, request, jsonify
from database import init_db, db_session, Customer, Loan, Payment
from datetime import datetime

app = Flask(__name__)


init_db()

@app.route('/')
def index():
    return "Welcome to the Bank System API!"

@app.route('/lend', methods=['POST'])
def lend():
    data = request.json
    customer_id = data['customer_id']
    principal = data['principal']
    loan_period = data['loan_period']
    interest_rate = data['interest_rate']
    
    interest = principal * loan_period * (interest_rate / 100)
    total_amount = principal + interest
    emi_amount = total_amount / (loan_period * 12)
    
    loan = Loan(customer_id=customer_id, principal=principal, interest=interest, 
                total_amount=total_amount, loan_period=loan_period, emi_amount=emi_amount,
                remaining_amount=total_amount, emis_left=loan_period * 12)
    
    db_session.add(loan)
    db_session.commit()
    
    return jsonify({
        'total_amount': total_amount,
        'emi_amount': emi_amount
    })

@app.route('/payment', methods=['POST'])
def payment():
    data = request.json
    loan_id = data['loan_id']
    payment_type = data['payment_type']
    amount = data['amount']
    
    loan = Loan.query.filter_by(id=loan_id).first()
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    
    payment = Payment(loan_id=loan_id, payment_type=payment_type, amount=amount, date=datetime.now())
    db_session.add(payment)
    
    if payment_type == 'EMI':
        loan.emis_left -= 1
        loan.remaining_amount -= loan.emi_amount
    elif payment_type == 'LUMP SUM':
        loan.remaining_amount -= amount
        loan.emis_left = loan.remaining_amount // loan.emi_amount
    
    db_session.commit()
    
    return jsonify({'remaining_amount': loan.remaining_amount, 'emis_left': loan.emis_left})

@app.route('/ledger/<int:loan_id>', methods=['GET'])
def ledger(loan_id):
    loan = Loan.query.filter_by(id=loan_id).first()
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    
    payments = Payment.query.filter_by(loan_id=loan_id).all()
    transactions = [{'amount': p.amount, 'type': p.payment_type, 'date': p.date} for p in payments]
    
    return jsonify({
        'transactions': transactions,
        'remaining_amount': loan.remaining_amount,
        'emi_amount': loan.emi_amount,
        'emis_left': loan.emis_left
    })

@app.route('/account_overview/<int:customer_id>', methods=['GET'])
def account_overview(customer_id):
    loans = Loan.query.filter_by(customer_id=customer_id).all()
    if not loans:
        return jsonify({'error': 'No loans found for customer'}), 404
    
    overview = []
    for loan in loans:
        paid_amount = sum([p.amount for p in Payment.query.filter_by(loan_id=loan.id).all()])
        overview.append({
            'loan_id': loan.id,
            'principal': loan.principal,
            'total_amount': loan.total_amount,
            'emi_amount': loan.emi_amount,
            'interest': loan.interest,
            'paid_amount': paid_amount,
            'emis_left': loan.emis_left
        })
    
    return jsonify(overview)

if __name__ == '__main__':
    app.run(debug=True)
