import os
import io
import qrcode
from flask import Flask, render_template, request, jsonify, send_file
from models import db, Customer, Transaction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playarea.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CHECKIN_FEE = 100.0

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/customers')
def customers_page():
    return render_template('customers.html')

@app.route('/recharge')
def recharge_page():
    return render_template('recharge.html')

@app.route('/scan')
def scan_page():
    return render_template('scan.html')

# API Endpoints

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_customers = Customer.query.count()
    total_revenue = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='checkin').scalar() or 0.0
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    return jsonify({
        'total_customers': total_customers,
        'total_revenue': abs(total_revenue),
        'recent_transactions': [{
            'id': t.id,
            'customer_name': t.customer.name,
            'amount': abs(t.amount),
            'type': t.type,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for t in recent_transactions]
    })

@app.route('/api/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'GET':
        customers = Customer.query.order_by(Customer.created_at.desc()).limit(100).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'balance': c.balance,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for c in customers])
    
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        initial_balance = float(data.get('initial_balance', 0.0))
        qr_id = data.get('qr_id')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
            
        if initial_balance < 0:
            return jsonify({'error': 'Initial balance cannot be negative'}), 400
            
        if qr_id:
            # Check if this QR ID already exists
            existing = Customer.query.get(qr_id)
            if existing:
                return jsonify({'error': 'This QR Code is already assigned to a customer.'}), 400
            new_customer = Customer(id=qr_id, name=name, balance=initial_balance)
        else:
            new_customer = Customer(name=name, balance=initial_balance)
            
        db.session.add(new_customer)
        if initial_balance > 0:
            db.session.flush() # Get the ID
            initial_tx = Transaction(customer_id=new_customer.id, amount=initial_balance, type='recharge')
            db.session.add(initial_tx)
            
        db.session.commit()
        return jsonify({'message': 'Customer created successfully', 'id': new_customer.id}), 201

@app.route('/api/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    Transaction.query.filter_by(customer_id=customer.id).delete()
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/api/customers/search', methods=['GET'])
def search_customers():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    customers = Customer.query.filter(Customer.name.ilike(f'%{q}%')).order_by(Customer.created_at.desc()).limit(15).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'balance': c.balance
    } for c in customers])

@app.route('/api/recharge', methods=['POST'])
def recharge():
    data = request.json
    customer_id = data.get('customer_id')
    amount = float(data.get('amount', 0.0))
    
    if not customer_id or amount <= 0:
        return jsonify({'error': 'Valid customer ID and amount are required'}), 400
        
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    customer.balance += amount
    tx = Transaction(customer_id=customer.id, amount=amount, type='recharge')
    db.session.add(tx)
    db.session.commit()
    
    return jsonify({'message': 'Recharge successful', 'new_balance': customer.balance}), 200

@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json
    customer_id = data.get('customer_id')
    
    if not customer_id:
        return jsonify({'error': 'Customer ID is required'}), 400
        
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    if customer.balance < CHECKIN_FEE:
        return jsonify({'error': f'Insufficient balance. Need ${CHECKIN_FEE}, but have ${customer.balance}'}), 400
        
    customer.balance -= CHECKIN_FEE
    tx = Transaction(customer_id=customer.id, amount=-CHECKIN_FEE, type='checkin')
    db.session.add(tx)
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in successful!',
        'customer_name': customer.name,
        'remaining_balance': customer.balance
    }), 200

@app.route('/qrcode/<customer_id>.png')
def generate_qr(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(customer.id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=5000)

    app.run(debug=True)