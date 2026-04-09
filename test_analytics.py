from app import app, db
from models import Customer, Transaction
from datetime import datetime
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.create_all()
    c = Customer(name='Tester', balance=1000)
    db.session.add(c)
    db.session.commit()
    
    now = datetime.utcnow()
    t1 = Transaction(customer_id=c.id, amount=-100, type='checkin')
    t1.created_at = now.replace(hour=1)
    t2 = Transaction(customer_id=c.id, amount=-100, type='checkin')
    t2.created_at = now.replace(hour=14)
    db.session.add_all([t1, t2])
    db.session.commit()

with app.test_client() as client:
    date_str = now.strftime('%Y-%m-%d')
    res = client.get(f'/api/analytics?interval=hourly&date={date_str}')
    data = res.get_json()
    assert sum(data['data']) == 2
    assert data['data'][1] == 1
    assert data['data'][14] == 1
    print('Hourly Check-in test passed!')
    
    res = client.get(f'/api/analytics?interval=daily&date={date_str}')
    data = res.get_json()
    assert sum(data['data']) == 2
    print(f"Daily Aggregation Week Context: {data['start']} to {data['end']}")
    print('Daily test passed!')
