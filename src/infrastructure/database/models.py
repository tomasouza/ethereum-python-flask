
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy() # Inicializado posteriormente com o app Flask

class AddressModel(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), unique=True, nullable=False)
    private_key = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AddressModel {self.address}>'

class ValidatedTransactionModel(db.Model):
    __tablename__ = 'validated_transactions'
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(66), unique=True, nullable=False)
    asset = db.Column(db.String(10), nullable=False)
    to_address = db.Column(db.String(42), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ValidatedTransactionModel {self.tx_hash}>'

class CreatedTransactionModel(db.Model):
    __tablename__ = 'created_transactions'
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(66), unique=True, nullable=True)
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42), nullable=False)
    asset = db.Column(db.String(10), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    gas_price_gwei = db.Column(db.String(50), nullable=True)
    gas_limit = db.Column(db.Integer, nullable=True)
    effective_cost_wei = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CreatedTransactionModel {self.tx_hash or self.id}>'


