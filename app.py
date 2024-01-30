from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pickle
import re
import bcrypt
app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'user_details'

mysql = MySQL(app)



# Generate a random secret key
secret_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
app.secret_key = secret_key

#pkl file import
model=pickle.load(open('model.pkl','rb'))

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    register_text=""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       
        # Define regex patterns for username and password
        username_pattern = r'^[a-zA-Z0-9_-]{3,16}$'
        password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-_=+])[a-zA-Z0-9!@#$%^&*()-_=+]{8,}$'

        # Check if the username matches the pattern
        if not re.match(username_pattern, username):
            return render_template("register.html",register_text="Username should be 3-16 characters long and can contain only letters, numbers, underscores, and hyphens.")

        # Check if the password matches the pattern
        if not re.match(password_pattern, password):
            return render_template("register.html",register_text="Password should be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character.")

        cur = mysql.connection.cursor()
        
        # Check if the username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return render_template("register.html",register_text="Username already exists. Please choose a different username.")
        
        encrypted_password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # If the username doesn't exist and the username and password are valid, proceed with registration
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, encrypted_password))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')
    return render_template('register.html',register_text=register_text)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print("password",password)
        
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", (username,))

        if result > 0:
            user = cur.fetchone()  
            stored_password=user[2]
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['logged_in'] = True
                session['username'] = username
                return redirect('/enter_details')
            else:
                return render_template('login.html',login_text="Login Failed !")
        else:
            return render_template('login.html',login_text="Login Failed !")
    return render_template('login.html',login_text="")




@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    pred_text=""
    if request.method == 'POST':
        gender_male = 1 if request.form['Gender'] == 'Male' else 0
        # gender_female = 1 if request.form['Gender'] == 'Female' else 0
        married_yes = 1 if request.form['married'] == 'Yes' else 0
        married_no = 1 if request.form['married'] == 'No' else 0
        dependents = float(request.form['dependents'])
        education = request.form['education']
        self_employed_yes = 1 if request.form['self_employed'] == 'Yes' else 0
        # self_employed_no = 1 if request.form['self_employed'] == 'No' else 0
        applicant_income = float(request.form['Applicant Income'])
        coapplicant_income = float(request.form['Coapplicant Income'])
        loan_amount = float(request.form['Loan Amount'])
        loan_amount_term = float(request.form['Loan Amount Term'])
        credit_history = float(request.form['Credit History'])
        property_area = request.form['Property Area']

        prediction = model.predict([[
            gender_male, married_yes, married_no,
            dependents, self_employed_yes, 
            applicant_income, coapplicant_income, loan_amount,
            loan_amount_term, credit_history, property_area
        ]])

        if prediction[0] == 1:
            pred_text = "Congratulations!! You are eligible for the loan."
        else:
            pred_text = "Sorry, you are not eligible for the loan."
        
        

            # # Retrieve user details from the form
            # income = request.form['income']
            # credit_score = request.form['credit_score']
            
            # # Perform loan eligibility prediction here

            # # Render prediction results template
            # return render_template('prediction_results.html', income=income, credit_score=credit_score)
        return render_template('predict.html',pred_text=pred_text)
    return render_template('predict.html',pred_text=pred_text)   


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
