from flask import Flask, render_template, redirect, request
from flask import current_app as app #directly importing app-> circular import error, current_app is the app object created in app.py
from .models import User, ParkingLot, ParkingSpot, Reserve, db

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        pwd=request.form["pass"]
        curr_user = User.query.filter_by(username=username).first()
        if curr_user:
            if curr_user.password == pwd:
                if curr_user.type == "admin":
                    return render_template("admin_dashboard.html", user=curr_user)
                else:
                    return render_template("user_dashboard.html", user=curr_user)
            else:
                return "Incorrect Password"
        else:
            return "User DNE"
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form["email"]
        password=request.form.get("password")
        address=request.form["address"]
        pincode=request.form['pincode']
        if User.query.filter_by(username=username).first():
            return "Username already exists, try registering with different username"
        else:
            new_user=User(username=username, email=email, password=password, address=address, pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
            return "Registered Successfully!"
    return render_template("register.html")
