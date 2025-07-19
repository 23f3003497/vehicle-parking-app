from flask import Flask, render_template, redirect, request, session
from flask import current_app as app #directly importing app-> circular import error, current_app is the app object created in app.py
from .models import User, ParkingLot, ParkingSpot, Reserve, db
from datetime import datetime
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        pwd=request.form["pass"]
        curr_user = User.query.filter_by(username=username).first()
        if curr_user:
            if curr_user.password == pwd:
                #session['username'] = curr_user.username
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

# @app.route("/user-search", methods=["GET"])
# def user_search():
#     username=session.get("username")
#     return render_template("user_search.html", username=username)

@app.route("/create-pklot", methods=["POST", "GET"])
def create_parkinglot():
    user = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        action=request.form.get("action")
        if action=="ADD":
            location=request.form.get("location")
            address=request.form.get("address")
            pph=int(request.form.get("price"))
            pincode=request.form.get("pin")
            max_spots=int(request.form.get("max-spots"))
            new_pkl = ParkingLot(prime_location_name=location, address=address, price=pph, pincode=pincode, max_spots=max_spots)
            db.session.add(new_pkl)
            db.session.commit()
            
            for i in range(max_spots):
                new_spot=ParkingSpot(lot_id=new_pkl.id)
                db.session.add(new_spot)
            db.session.commit()
        return render_template("admin_dashboard.html", user=user)
    return render_template("create_parkinglot.html")

@app.route("/search-pklot/<int:user_id>", methods=["POST"])
def search_parkinglot(user_id):
    user=User.query.get(user_id)
    location = request.form.get("loc")
    pklots=ParkingLot.query.filter_by(prime_location_name = location).all()
    return render_template("display_parkinglots.html", loc=location, pklots=pklots, user=user)

@app.route("/book-pkspot/<int:lot_id>/<int:user_id>", methods=["GET", "POST"])
def book_parkingspot(lot_id, user_id):
    if request.method=="GET":
        pklot=ParkingLot.query.get(lot_id)
        first_av_spot=ParkingSpot.query.filter_by(lot_id = lot_id, status="Available").first()
        return render_template("reserve_lot.html", lot_id=lot_id, user_id=user_id, spot_id=first_av_spot.id, pklot=pklot)
    if request.method=="POST":
        user=User.query.get(user_id)
        action=request.form.get("action")
        if action=="BOOK":
            
            spot_id=request.form.get("spot_id")
            time=datetime.now()
            vehicle_no=request.form.get("vehicle_number")
            price=request.form.get("price")
            new_booking=Reserve(spot_id=spot_id, user_id=user_id, vehicle_number=vehicle_no, parking_timestamp=time, parking_cost=price)
            spot=ParkingSpot.query.get(spot_id)
            spot.status="Booked"
            db.session.add(new_booking)
            db.session.commit()
        return render_template("user_dashboard.html", user=user)
    
@app.route("/display_users")
def display_registered_users():
    users=User.query.all()
    return render_template("display_users.html",users=users)





