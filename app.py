from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Database model for Employee
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)

# User model for login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Home route with login form
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':  # Simple validation (replace with proper auth)
        user = User(id=1)
        login_user(user)
        flash('Login successful!', 'success')  # Added success message
        return redirect(url_for('admin_dashboard'))
    flash('Invalid credentials', 'danger')
    return redirect(url_for('index'))


# Admin Dashboard route (protected)
@app.route('/dashboard')
@login_required
def admin_dashboard():
    employees = Employee.query.all()
    return render_template('dashboard.html', employees=employees)

# Add Employee route
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        new_employee = Employee(name=name, email=email, position=position)
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_employee.html')

# Update Employee route
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.position = request.form['position']
        db.session.commit()
        flash('Employee updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('update_employee.html', employee=employee)

# Delete Employee route
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted!', 'danger')
    return redirect(url_for('admin_dashboard'))

# Logout route

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')  # Added logout message
    return redirect(url_for('index'))


# Ensure database is created within the app context
if __name__ == '__main__':
    with app.app_context():  # Using app context to ensure db operations run within the app context
        db.create_all()
    app.run(debug=True)
