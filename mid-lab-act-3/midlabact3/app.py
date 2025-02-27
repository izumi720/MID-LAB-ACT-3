from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# ✅ Configure PostgreSQL for Records & SQLite for Logs
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres_db'
app.config['SQLALCHEMY_BINDS'] = {'logs': 'sqlite:///logs.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize SQLAlchemy (Single Instance for Both Databases)
db = SQLAlchemy(app)

# ✅ PostgreSQL Model (Records)
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)

# ✅ SQLite Model (Logs)
class Log(db.Model):
    __bind_key__ = 'logs'  # Use 'logs' bind for SQLite
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ✅ Create Tables for Both Databases
with app.app_context():
    db.create_all()

# ✅ Route: Home (Displays All Records)
@app.route('/')
def index():
    records = Record.query.all()
    return render_template('index.html', records=records)

# ✅ Route: View Logs Page
@app.route('/view-logs')
def logs_page():
    logs = Log.query.all()
    return render_template('logs.html', logs=logs)

# ✅ API: Create Record
@app.route('/create', methods=['POST'])
def create_record():
    data = request.json
    new_record = Record(name=data['name'], description=data['description'])
    db.session.add(new_record)
    db.session.commit()

    log_action("Created record")
    return jsonify({'message': 'Record created successfully'})

# ✅ API: Read Records (JSON Response)
@app.route('/read', methods=['GET'])
def read_records():
    records = Record.query.all()
    return jsonify([{'id': r.id, 'name': r.name, 'description': r.description} for r in records])

# ✅ API: Update Record
@app.route('/update/<int:id>', methods=['PUT'])
def update_record(id):
    record = Record.query.get(id)
    if not record:
        return jsonify({'message': 'Record not found'}), 404

    data = request.json
    record.name = data['name']
    record.description = data['description']
    db.session.commit()

    log_action("Updated record")
    return jsonify({'message': 'Record updated successfully'})

# ✅ API: Delete Record
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_record(id):
    record = Record.query.get(id)
    if not record:
        return jsonify({'message': 'Record not found'}), 404

    db.session.delete(record)
    db.session.commit()

    log_action("Deleted record")
    return jsonify({'message': 'Record deleted successfully'})

# ✅ API: Get Logs (JSON Response)
@app.route('/logs', methods=['GET'])
def get_logs():
    logs = Log.query.all()
    return jsonify([{'id': log.id, 'action': log.action, 'timestamp': log.timestamp} for log in logs])

# ✅ Function: Log Actions
def log_action(action):
    log_entry = Log(action=action)
    db.session.add(log_entry)  # Uses the same db session
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
