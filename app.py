from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import inspect, text
import csv
import io
import os
import secrets
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helpdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

DEFAULT_ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@stjtid.edu')
DEFAULT_ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@12345')

# Role definitions
ROLE_CHOICES = [
    'admin',
    'staff',
    'student',
    'support_staff',
    'technician',
    'digital_specialist',
    'web_master',
    'user'
]
STAFF_ROLES = {'admin', 'staff', 'support_staff', 'technician', 'digital_specialist', 'web_master'}

# ERP modules supported for ticketing
ERP_MODULES = [
    'finance',
    'human_resources',
    'inventory',
    'payroll',
    'procurement',
    'admissions',
    'student_records',
    'examinations',
    'other'
]

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_staff = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    module = db.Column(db.String(80), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    response = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('tickets', lazy=True, cascade='all, delete-orphan'))
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref=db.backref('assigned_tickets', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ticket = db.relationship('Ticket', backref='messages')
    sender = db.relationship('User')

# Authentication helpers
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_staff:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')


def ensure_database_schema():
    inspector = inspect(db.engine)
    if 'ticket' not in inspector.get_table_names():
        return

    ticket_columns = {column['name'] for column in inspector.get_columns('ticket')}
    if 'assigned_staff_id' not in ticket_columns:
        db.session.execute(text('ALTER TABLE ticket ADD COLUMN assigned_staff_id INTEGER'))
        db.session.commit()
    if 'module' not in ticket_columns:
        db.session.execute(text("ALTER TABLE ticket ADD COLUMN module VARCHAR"))
        db.session.commit()

    # Ensure `role` column exists on user table for role support
    if 'user' in inspector.get_table_names():
        user_columns = {column['name'] for column in inspector.get_columns('user')}
        if 'role' not in user_columns:
            # SQLite allows adding a column with a DEFAULT
            db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR DEFAULT 'user'"))
            db.session.commit()
            # Backfill is_staff based on role where applicable
            try:
                db.session.execute(text("UPDATE user SET is_staff = 1 WHERE role IN ('admin','staff','support_staff','technician','digital_specialist','web_master')"))
                db.session.commit()
            except Exception:
                db.session.rollback()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='user',
            is_staff=False
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_staff'] = user.is_staff
            session['role'] = user.role
            
            if user.is_staff:
                return jsonify({'redirect': url_for('admin_dashboard')}), 200
            return jsonify({'redirect': url_for('my_tickets')}), 200
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/submit-ticket', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    if request.method == 'POST':
        data = request.get_json()
        ticket = Ticket(
            user_id=session['user_id'],
            module=data.get('module'),
            subject=data.get('subject'),
            description=data.get('description'),
            category=data.get('category'),
            priority=data.get('priority', 'normal')
        )
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({'message': 'Ticket submitted successfully', 'ticket_id': ticket.id}), 201
    
    return render_template('submit_ticket.html')

@app.route('/my-tickets')
@login_required
def my_tickets():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.filter_by(user_id=session['user_id']).order_by(Ticket.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('my_tickets.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != session['user_id'] and not session.get('is_staff'):
        return redirect(url_for('index'))
    
    messages = Message.query.filter_by(ticket_id=ticket_id).all()
    staff_users = User.query.filter(User.role.in_(list(STAFF_ROLES))).order_by(User.username).all()
    return render_template('ticket_detail.html', ticket=ticket, messages=messages, staff_users=staff_users)

@app.route('/api/ticket/<int:ticket_id>/message', methods=['POST'])
@login_required
def add_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != session['user_id'] and not session.get('is_staff'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    message = Message(
        ticket_id=ticket_id,
        user_id=session['user_id'],
        content=data.get('content')
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'message': 'Message added successfully'}), 201

@app.route('/admin')
@staff_required
def admin_dashboard():
    open_tickets = Ticket.query.filter_by(status='open').count()
    resolved_tickets = Ticket.query.filter_by(status='resolved').count()
    assigned_tickets = Ticket.query.filter(Ticket.assigned_staff_id.isnot(None)).count()
    total_users = User.query.count()
    staff_users = User.query.filter_by(is_staff=True).order_by(User.username).all()
    
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         open_tickets=open_tickets,
                         resolved_tickets=resolved_tickets,
                         assigned_tickets=assigned_tickets,
                         total_users=total_users,
                         staff_users=staff_users,
                         recent_tickets=recent_tickets)

@app.route('/admin/tickets')
@staff_required
def admin_tickets():
    status = request.args.get('status', 'open')
    page = request.args.get('page', 1, type=int)
    
    tickets = Ticket.query.filter_by(status=status).order_by(Ticket.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin_tickets.html', tickets=tickets, status=status)


@app.route('/admin/ticket/<int:ticket_id>/update', methods=['POST'])
@staff_required
def admin_update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    priority = request.form.get('priority', '').strip()
    status_value = request.form.get('status', '').strip()
    response = request.form.get('response', '').strip()
    assigned_staff_id = request.form.get('assigned_staff_id', '').strip()

    if subject:
        ticket.subject = subject
    if description:
        ticket.description = description
    if category:
        ticket.category = category
    if priority:
        ticket.priority = priority
    if status_value:
        ticket.status = status_value
        if status_value == 'resolved' and ticket.resolved_at is None:
            ticket.resolved_at = datetime.utcnow()
        elif status_value != 'resolved':
            ticket.resolved_at = None
    if response:
        ticket.response = response

    if assigned_staff_id:
        assigned_staff = User.query.filter_by(id=int(assigned_staff_id), is_staff=True).first()
        if assigned_staff:
            ticket.assigned_staff_id = assigned_staff.id
    else:
        ticket.assigned_staff_id = None

    ticket.updated_at = datetime.utcnow()
    db.session.commit()

    session['message'] = f'Ticket #{ticket.id} updated successfully.'
    return redirect(url_for('view_ticket', ticket_id=ticket.id))


@app.route('/admin/ticket/<int:ticket_id>/delete', methods=['POST'])
@staff_required
def admin_delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    Message.query.filter_by(ticket_id=ticket.id).delete(synchronize_session=False)
    db.session.delete(ticket)
    db.session.commit()

    session['message'] = f'Ticket #{ticket_id} deleted.'
    return redirect(url_for('admin_tickets'))

@app.route('/api/ticket/<int:ticket_id>/update', methods=['PUT'])
@staff_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    if 'status' in data:
        ticket.status = data['status']
        if data['status'] == 'resolved':
            ticket.resolved_at = datetime.utcnow()
    
    if 'priority' in data:
        ticket.priority = data['priority']
    
    if 'response' in data:
        ticket.response = data['response']
    
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Ticket updated successfully'}), 200

@app.route('/admin/users')
@staff_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin_users.html', users=users, default_admin_username=DEFAULT_ADMIN_USERNAME)


@app.route('/admin/user/<int:user_id>/reset-password', methods=['POST'])
@staff_required
def admin_reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '').strip() or secrets.token_urlsafe(8)
    user.password = generate_password_hash(new_password)
    db.session.commit()

    session['message'] = f'Password reset for {user.username}. Temporary password: {new_password}'
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@staff_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == DEFAULT_ADMIN_USERNAME:
        session['error'] = 'The system admin account cannot be deleted.'
        return redirect(url_for('admin_users'))

    if user.id == session.get('user_id'):
        session['error'] = 'You cannot delete your own active account.'
        return redirect(url_for('admin_users'))

    user_ticket_ids = [ticket.id for ticket in user.tickets]
    if user_ticket_ids:
        Message.query.filter(Message.ticket_id.in_(user_ticket_ids)).delete(synchronize_session=False)
    Message.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()

    session['message'] = f'User {user.username} deleted.'
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/assign-role', methods=['POST'])
@admin_required
def admin_assign_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', '').strip()

    if new_role not in ROLE_CHOICES:
        session['error'] = 'Invalid role selected.'
        return redirect(url_for('admin_users'))

    # Prevent deleting or demoting the system admin username
    if user.username == DEFAULT_ADMIN_USERNAME and new_role != 'admin':
        session['error'] = 'Cannot change role of the system admin account.'
        return redirect(url_for('admin_users'))

    user.role = new_role
    user.is_staff = True if new_role in STAFF_ROLES else False
    db.session.commit()

    # Update session role if admin changed own role
    if user.id == session.get('user_id'):
        session['role'] = user.role
        session['is_staff'] = user.is_staff

    session['message'] = f'Role for {user.username} set to {user.role}.'
    return redirect(url_for('admin_users'))


def build_ticket_report_rows():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    rows = []
    for ticket in tickets:
        rows.append({
            'module': ticket.module or '',
            'ticket_id': ticket.id,
            'subject': ticket.subject,
            'category': ticket.category,
            'priority': ticket.priority,
            'status': ticket.status,
            'requester': ticket.user.username if ticket.user else '',
            'assigned_staff': ticket.assigned_staff.username if ticket.assigned_staff else '',
            'created_at': ticket.created_at.isoformat(sep=' ', timespec='seconds'),
            'updated_at': ticket.updated_at.isoformat(sep=' ', timespec='seconds') if ticket.updated_at else '',
            'resolved_at': ticket.resolved_at.isoformat(sep=' ', timespec='seconds') if ticket.resolved_at else '',
            'response': ticket.response or ''
        })
    return rows


@app.route('/admin/reports/tickets.csv')
@app.route('/admin/reports/tickets.<report_format>')
@staff_required
def download_ticket_report(report_format='csv'):
    rows = build_ticket_report_rows()

    if report_format == 'json':
        return jsonify({
            'generated_at': datetime.utcnow().isoformat(sep=' ', timespec='seconds'),
            'total_tickets': len(rows),
            'tickets': rows,
        })

    if report_format == 'txt':
        output = io.StringIO()
        output.write('STJTID Institute Helpdesk Ticket Report\n')
        output.write(f'Generated: {datetime.utcnow().isoformat(sep=" ", timespec="seconds")}\n')
        output.write(f'Total tickets: {len(rows)}\n\n')
        for row in rows:
            output.write(f"Ticket #{row['ticket_id']} | {row['subject']}\n")
            output.write(f"Category: {row['category']}\n")
            output.write(f"Priority: {row['priority']}\n")
            output.write(f"Status: {row['status']}\n")
            output.write(f"Requester: {row['requester']}\n")
            output.write(f"Assigned Staff: {row['assigned_staff'] or 'Unassigned'}\n")
            output.write(f"Created At: {row['created_at']}\n")
            output.write(f"Updated At: {row['updated_at']}\n")
            output.write(f"Resolved At: {row['resolved_at'] or 'N/A'}\n")
            output.write(f"Response: {row['response'] or 'N/A'}\n")
            output.write('-' * 60 + '\n')

        return Response(
            output.getvalue(),
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment; filename=helpdesk_ticket_report.txt'}
        )

    if report_format != 'csv':
        abort(404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Ticket ID', 'Subject', 'Category', 'Priority', 'Status', 'Requester',
        'Assigned Staff', 'Created At', 'Updated At', 'Resolved At', 'Response'
    ])

    for row in rows:
        writer.writerow([
            row['ticket_id'],
            row['subject'],
            row['category'],
            row['priority'],
            row['status'],
            row['requester'],
            row['assigned_staff'],
            row['created_at'],
            row['updated_at'],
            row['resolved_at'],
            row['response']
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=helpdesk_ticket_report.csv'}
    )

# API for getting ticket stats
@app.route('/api/stats')
@staff_required
def get_stats():
    stats = {
        'total_tickets': Ticket.query.count(),
        'open_tickets': Ticket.query.filter_by(status='open').count(),
        'in_progress': Ticket.query.filter_by(status='in_progress').count(),
        'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
        'total_users': User.query.count()
    }
    return jsonify(stats)


def ensure_default_admin():
    admin_user = User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()
    if admin_user:
        changed = False
        if not admin_user.is_staff:
            admin_user.is_staff = True
            changed = True
        if admin_user.role != 'admin':
            admin_user.role = 'admin'
            changed = True
        if changed:
            db.session.commit()
        return

    admin_user = User(
        username=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        password=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        is_staff=True,
        role='admin'
    )
    db.session.add(admin_user)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_database_schema()
        ensure_default_admin()
    # Bind to 0.0.0.0 for local network access
    app.run(host='0.0.0.0', port=5000, debug=True)
