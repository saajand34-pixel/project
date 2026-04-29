from flask import Flask, render_template, request, redirect, session
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "secret123"

# Dummy ML model (simple training)
X = np.array([[1,60],[2,65],[3,70],[4,75],[5,80]])
y = np.array([40,45,50,55,65])

model = LinearRegression()
model.fit(X,y)

# Create DB
def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' in session:
        return render_template("index.html")
    return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect("users.db")
        conn.execute("INSERT INTO users (username,password) VALUES (?,?)",(user,pwd))
        conn.commit()
        conn.close()

        return redirect('/login')
    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(user,pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session['user'] = user
            return redirect('/')
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")

@app.route('/predict', methods=['POST'])
def predict():
    hours = float(request.form['study_hours'])
    att = float(request.form['attendance'])

    pred = model.predict([[hours, att]])
    result = f"Predicted Marks: {round(pred[0],2)}"

    return render_template("index.html", prediction_text=result)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)