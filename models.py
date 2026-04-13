from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

def get_ist_time():
    from datetime import timedelta
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class Customer(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=get_ist_time, index=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False, index=True) # 'recharge' or 'checkin'
    created_at = db.Column(db.DateTime, default=get_ist_time, index=True)

    customer = db.relationship('Customer', backref=db.backref('transactions', lazy=True, order_by='Transaction.created_at.desc()'))

    # Composite index: analytics queries always filter on both type AND created_at together
    __table_args__ = (
        db.Index('ix_tx_type_created', 'type', 'created_at'),
    )

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
