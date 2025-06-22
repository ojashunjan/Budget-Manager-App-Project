from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import cs50

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_transaction = Transaction(description=description, amount=amount, category=category, date=date)
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('index'))

    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    total_spent = db.session.query(func.sum(Transaction.amount)).scalar() or 0

    return render_template('index.html', transactions=transactions, total_spent=total_spent)

@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        transaction.description = request.form['description']
        transaction.amount = float(request.form['amount'])
        transaction.category = request.form['category']
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', transaction=transaction)

@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
