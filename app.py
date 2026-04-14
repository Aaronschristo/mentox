import os
import io
import functools
import qrcode
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, make_response, send_from_directory
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models import db, Customer, Transaction, Setting, get_ist_time

app = Flask(__name__, static_folder='frontend', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playarea.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable aggressive caching for dev

db.init_app(app)
CORS(app)  # Allow cross-origin requests from Tauri app and website

with app.app_context():
    db.create_all()
    
    defaults = {
        'checkin_fee': '100.0',
        'currency_symbol': '₹',
        'business_name': 'Venuity'
    }
    for k, v in defaults.items():
        if not db.session.get(Setting, k):
            db.session.add(Setting(key=k, value=v))
    db.session.commit()

@app.context_processor
def inject_settings():
    try:
        settings = {s.key: s.value for s in Setting.query.all()}
        return dict(settings=settings)
    except:
        return dict(settings={})

# --- QR Code In-Memory Cache ---
# QR content for a given customer ID never changes, so we generate once and cache forever.
@functools.lru_cache(maxsize=512)
def _generate_qr_png(customer_id: str) -> bytes:
    """Generate a QR code PNG. Cached per customer_id — only computed once."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(customer_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()

# Serve frontend static files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/customers')
def customers_page():
    return send_from_directory('frontend', 'customers.html')

@app.route('/recharge')
def recharge_page():
    return send_from_directory('frontend', 'recharge.html')

@app.route('/scan')
def scan_page():
    return send_from_directory('frontend', 'scan.html')

@app.route('/analytics')
def analytics_page():
    return send_from_directory('frontend', 'analytics.html')

@app.route('/settings')
def settings_page():
    return send_from_directory('frontend', 'settings.html')

# Serve any other static file in frontend/ (css, js, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend', filename)

# Serve files from the downloads folder
@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory('downloads', filename)

# API Endpoints

@app.route('/api/latest_installer', methods=['GET'])
def get_latest_installer():
    downloads_dir = 'downloads'
    if not os.path.exists(downloads_dir):
        return jsonify({'error': 'No downloads available'}), 404
        
    # Find all Venuity installers (.exe prioritised)
    files = [f for f in os.listdir(downloads_dir) if f.startswith('Venuity') and f.endswith(('.exe', '.msi'))]
    
    if not files:
        return jsonify({'error': 'No installers found'}), 404
        
    # Sort descending to get the latest version (e.g., 1.1.0 > 1.0.9)
    # This works for standard versioning strings
    files.sort(reverse=True)
    
    latest_file = files[0]
    return jsonify({
        'filename': latest_file,
        'url': f'/downloads/{latest_file}',
        'version': latest_file.split('_')[1] if '_' in latest_file else 'unknown'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_customers = Customer.query.count()
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(type='checkin').scalar() or 0.0

    # Fix: joinedload fetches all customer names in a single JOIN — eliminates N+1 queries
    recent_transactions = (
        Transaction.query
        .options(joinedload(Transaction.customer))
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    resp = make_response(jsonify({
        'total_customers': total_customers,
        'total_revenue': abs(total_revenue),
        'recent_transactions': [{
            'id': t.id,
            'customer_name': t.customer.name,
            'amount': abs(t.amount),
            'type': t.type,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for t in recent_transactions]
    }))
    resp.headers['Cache-Control'] = 'private, max-age=30'
    return resp

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    transactions = (
        Transaction.query
        .options(joinedload(Transaction.customer))
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    resp = make_response(jsonify([{
        'id': t.id,
        'customer_name': t.customer.name,
        'amount': abs(t.amount),
        'type': t.type,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for t in transactions]))
    resp.headers['Cache-Control'] = 'private, max-age=30'
    return resp

@app.route('/api/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'GET':
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 10, type=int)
        customers = Customer.query.order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()
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
            # Fix: db.session.get() — SQLAlchemy 2.x native API (checks identity map first)
            existing = db.session.get(Customer, qr_id)
            if existing:
                return jsonify({'error': 'This QR Code is already assigned to a customer.'}), 400
            new_customer = Customer(id=qr_id, name=name, balance=initial_balance)
        else:
            new_customer = Customer(name=name, balance=initial_balance)

        db.session.add(new_customer)
        if initial_balance > 0:
            db.session.flush()  # Get the ID
            initial_tx = Transaction(customer_id=new_customer.id, amount=initial_balance, type='recharge')
            db.session.add(initial_tx)

        db.session.commit()
        return jsonify({'message': 'Customer created successfully', 'id': new_customer.id}), 201

@app.route('/api/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)  # Fix: SQLAlchemy 2.x API
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    Transaction.query.filter_by(customer_id=customer.id).delete()
    db.session.delete(customer)
    db.session.commit()

    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/api/customers/search', methods=['GET'])
def search_customers():
    q = request.args.get('q', '').strip()
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    if not q:
        return jsonify([])
    customers = Customer.query.filter(Customer.name.ilike(f'%{q}%')).order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'balance': c.balance,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for c in customers])

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    interval = request.args.get('interval', 'hourly')
    metric = request.args.get('metric', 'customers')
    target_date_str = request.args.get('date')

    if not target_date_str:
        target_date = get_ist_time()
    else:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if interval == 'hourly':
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        agg_func = func.sum(Transaction.amount) if metric == 'revenue' else func.count(Transaction.id)

        # Fix: GROUP BY in the database — returns at most 24 rows instead of all transactions
        results = db.session.query(
            func.strftime('%H', Transaction.created_at).label('hour'),
            agg_func.label('val')
        ).filter(
            Transaction.type == 'checkin',
            Transaction.created_at >= start_of_day,
            Transaction.created_at < end_of_day
        ).group_by('hour').all()

        hourly_counts = [0] * 24
        for row in results:
            val = row.val or 0
            if metric == 'revenue': val = abs(val)
            hourly_counts[int(row.hour)] += val

        return jsonify({
            'labels': [f'{h:02d}:00' for h in range(24)],
            'data': hourly_counts,
            'start': start_of_day.strftime('%Y-%m-%d'),
            'end': start_of_day.strftime('%Y-%m-%d')
        })

    elif interval == 'daily':
        start_of_week = target_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        agg_func = func.sum(Transaction.amount) if metric == 'revenue' else func.count(Transaction.id)

        # Fix: GROUP BY in the database — returns at most 7 rows instead of all transactions
        # SQLite %w: 0=Sunday, 1=Monday, ..., 6=Saturday
        results = db.session.query(
            func.strftime('%w', Transaction.created_at).label('weekday'),
            agg_func.label('val')
        ).filter(
            Transaction.type == 'checkin',
            Transaction.created_at >= start_of_week,
            Transaction.created_at < end_of_week
        ).group_by('weekday').all()

        daily_counts = [0] * 7
        for row in results:
            val = row.val or 0
            if metric == 'revenue': val = abs(val)
            # Convert SQLite weekday (0=Sun..6=Sat) → Python weekday (0=Mon..6=Sun)
            sqlite_day = int(row.weekday)
            python_day = (sqlite_day - 1) % 7
            daily_counts[python_day] += val

        return jsonify({
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': daily_counts,
            'start': start_of_week.strftime('%Y-%m-%d'),
            'end': (end_of_week - timedelta(days=1)).strftime('%Y-%m-%d')
        })

    return jsonify({'error': 'Invalid interval'}), 400

@app.route('/api/recharge', methods=['POST'])
def recharge():
    data = request.json
    customer_id = data.get('customer_id')
    amount = float(data.get('amount', 0.0))

    if not customer_id or amount <= 0:
        return jsonify({'error': 'Valid customer ID and amount are required'}), 400

    customer = db.session.get(Customer, customer_id)  # Fix: SQLAlchemy 2.x API
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

    customer = db.session.get(Customer, customer_id)  # Fix: SQLAlchemy 2.x API
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    fee_setting = db.session.get(Setting, 'checkin_fee')
    checkin_fee = float(fee_setting.value) if fee_setting else 100.0

    if customer.balance < checkin_fee:
        return jsonify({'error': f'Insufficient balance. Need {checkin_fee}, but have {customer.balance}'}), 400

    customer.balance -= checkin_fee
    tx = Transaction(customer_id=customer.id, amount=-checkin_fee, type='checkin')
    db.session.add(tx)
    db.session.commit()

    return jsonify({
        'message': 'Check-in successful!',
        'customer_name': customer.name,
        'remaining_balance': customer.balance
    }), 200

@app.route('/api/settings_get', methods=['GET'])
def get_settings():
    """GET endpoint for the frontend to load current settings as JSON."""
    settings = {s.key: s.value for s in Setting.query.all()}
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.json
    for k, v in data.items():
        setting = db.session.get(Setting, k)
        if setting:
            setting.value = str(v)
    db.session.commit()
    return jsonify({'message': 'Settings saved successfully'}), 200

@app.route('/qrcode/<customer_id>.png')
def generate_qr(customer_id):
    db.get_or_404(Customer, customer_id)  # 404 if customer doesn't exist

    # Fix: serve from in-memory cache — only generates once per unique customer ID
    png_bytes = _generate_qr_png(customer_id)
    response = send_file(io.BytesIO(png_bytes), mimetype='image/png')
    response.headers['Cache-Control'] = 'public, max-age=86400'  # Browser caches for 24h
    return response

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

    # app.run(debug=True)