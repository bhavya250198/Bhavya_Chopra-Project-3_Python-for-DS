from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'user_details'

mysql = MySQL(app)

# Secret key for session management
app.secret_key = 'your_secret_key'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        
        # Check if the username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return "Username already exists. Please choose a different username."

        # If the username doesn't exist, proceed with registration
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))

        if result > 0:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/enter_details')
        else:
            return 'Login failed'
    return render_template('login.html')


@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    if 'logged_in' in session:
        if request.method == 'POST':
            # Retrieve user details from the form
            income = request.form['income']
            credit_score = request.form['credit_score']
            
            # Perform loan eligibility prediction here

            # Render prediction results template
            return render_template('prediction_results.html', income=income, credit_score=credit_score)
        return render_template('predict.html')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
