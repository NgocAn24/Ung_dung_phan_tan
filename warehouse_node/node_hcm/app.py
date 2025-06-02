from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders_hcm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'region': self.region,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Warehouse HCM node is running"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Get current order count as a basic load metric
        order_count = Order.query.count()
        return jsonify({
            'status': 'healthy',
            'node': 'HCM',
            'current_load': order_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/order', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['order_id', 'customer_name', 'region']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400

        # Create new order
        order = Order(
            order_id=data['order_id'],
            customer_name=data['customer_name'],
            region=data['region'],
            status='received'
        )
        
        db.session.add(order)
        db.session.commit()
        
        logger.info(f"Created order: {order.order_id}")
        return jsonify(order.to_dict()), 201

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create order',
            'details': str(e)
        }), 500

@app.route('/orders', methods=['GET'])
def list_orders():
    """List all orders"""
    try:
        orders = Order.query.all()
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        return jsonify({
            'error': 'Failed to list orders',
            'details': str(e)
        }), 500

@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({
                'error': 'Order not found'
            }), 404
        return jsonify(order.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve order',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
