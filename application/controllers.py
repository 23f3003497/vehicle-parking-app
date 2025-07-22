from flask import Flask, render_template, redirect, request, session, url_for
from flask import current_app as app #directly importing app-> circular import error, current_app is the app object created in app.py
from .models import User, ParkingLot, ParkingSpot, Reserve, db
from datetime import datetime
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        user_id=User.query.filter_by(username=username).first().id
        pwd=request.form["pass"]
        curr_user = User.query.filter_by(username=username).first()
        if curr_user:
            if curr_user.password == pwd:
                #session['username'] = curr_user.username
                if curr_user.type == "admin":
                    pklots=ParkingLot.query.all()
                    return render_template("admin_dashboard.html", user=curr_user, pklots=pklots)
                else:
                    return redirect(url_for("user_dashboard", user_id=user_id))
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
@app.route("/admin-dashboard")
def admin_dashboard():
    user = User.query.filter_by(type="admin").first()
    pklots = ParkingLot.query.all()
    return render_template("admin_dashboard.html", user=user, pklots=pklots)

@app.route("/user_dashboard/<int:user_id>")
def user_dashboard(user_id):
    l=[]
    user=User.query.get(user_id)
    reservations=Reserve.query.filter_by(user_id=user_id).all()
    for reservation in reservations:
        res_id=reservation.id
        spot=ParkingSpot.query.filter_by(id=reservation.spot_id).first()
        lot_id=spot.lot_id
        lot_loc=ParkingLot.query.filter_by(id=lot_id).first().prime_location_name
        vehicle_no=reservation.vehicle_number
        timestamp=reservation.parking_timestamp
        if spot.status=="Booked":
            action="Release"
        else:
            action="Reebook"
        l.append((res_id,lot_loc,vehicle_no,timestamp,action))

    return render_template("user_dashboard.html", user=user, res_list=l)


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
            #Prevent resubmission by redirecting
        return redirect(url_for('admin_dashboard'))
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
        action=request.form.get("action")
        if action=="BOOK":
            lot=ParkingLot.query.get(lot_id)
            if lot.occ_spots<lot.max_spots:
                lot.occ_spots = lot.occ_spots+1
                spot_id=request.form.get("spot_id")
                time=datetime.now()
                vehicle_no=request.form.get("vehicle_number")
                price=request.form.get("price")
                new_booking=Reserve(spot_id=spot_id, user_id=user_id, vehicle_number=vehicle_no, parking_timestamp=time, parking_cost=price)
                spot=ParkingSpot.query.get(spot_id)
                spot.status="Booked"
                db.session.add(new_booking)
                db.session.commit()
            else:
                return "No empty spots"
        return redirect(url_for('user_dashboard',user_id=user_id))
    
@app.route("/display_users")
def display_registered_users():
    users=User.query.all()
    return render_template("display_users.html",users=users)

@app.route("/delete_pklot/<int:lot_id>")
def delete_pklot(lot_id):
    pklot=ParkingLot.query.get(lot_id)
    if pklot.occ_spots == 0:
        pkspots=ParkingSpot.query.filter_by(id=lot_id).all()
        for spot in pkspots:
            db.session.delete(spot)
        db.session.delete(pklot)
        db.session.commit()
    else:
        return "can't delete lot with occupied spots"
    return redirect(url_for('admin_dashboard'))

#only the price per hour of a parking space can be edited
@app.route("/edit_pklot/<int:lot_id>", methods=["GET", "POST"])
def edit_pklot(lot_id):
    if request.method=="GET":
        pklot=ParkingLot.query.get(lot_id)
        return render_template("edit_parkinglot.html", pklot=pklot)
    if request.method=="POST":
        action=request.form.get("action")
        if action=="UPDATE":
            pklot=ParkingLot.query.get(lot_id)
            pklot.price = request.form.get("price")
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

@app.route("/search_lots", methods=["GET", "POST"])
def search_lots():
    if request.method=="GET":
        return render_template("search_lots.html", pklots=None)
    if request.method=="POST":
        category=request.form.get('category')
        cat_val=request.form.get("category_value")
        if category=="Lot ID":
            pklots=ParkingLot.query.filter_by(id=cat_val).all()  
        if category=="Prime Location":
            pklots=ParkingLot.query.filter_by(prime_location_name=cat_val).all()
        if category=="Address":
            pklots=ParkingLot.query.filter_by(address=cat_val).all()
        return render_template("search_lots.html", pklots=pklots)
        
    


    







