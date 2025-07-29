from flask import Flask, render_template, redirect, request, session, url_for
from flask import current_app as app #directly importing app-> circular import error, current_app is the app object created in app.py
from sqlalchemy import null
from .models import User, ParkingLot, ParkingSpot, Reserve, db
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        pwd=request.form["pass"]
        curr_user = User.query.filter_by(username=username).first()
        if curr_user:
            if curr_user.password == pwd:
                user_id=User.query.filter_by(username=username).first().id
                #session['username'] = curr_user.username
                if curr_user.type == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("user_dashboard", user_id=user_id))
            else:
                return render_template("incorr_pwd.html")
        else:
            return render_template("user_dne.html")
        
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
            return render_template("username_exists.html")
        else:
            new_user=User(username=username, email=email, password=password, address=address, pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
            return render_template('reg_success.html')
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
        spot_id=spot.id
        lot_id=spot.lot_id
        lot_loc=ParkingLot.query.filter_by(id=lot_id).first().prime_location_name
        vehicle_no=reservation.vehicle_number
        timestamp=reservation.parking_timestamp
        if reservation.leaving_timestamp:
            action="Parked Out"
        else:
            action="Release"
        l.append((res_id,spot_id,lot_loc,vehicle_no,timestamp,action))

    return render_template("user_dashboard.html", user=user, res_list=l)


@app.route("/create-pklot", methods=["POST", "GET"])
def create_parkinglot():
    #user = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        action=request.form.get("action")
        if action=="ADD":

            location=request.form.get("location")
            address=request.form.get("address")
            pph=int(request.form.get("price"))
            pincode=request.form.get("pin")
            max_spots=int(request.form.get("max-spots"))
            new_pkl = ParkingLot(prime_location_name=location, address=address, pincode=pincode, max_spots=max_spots)
            db.session.add(new_pkl)
            db.session.commit()
            for i in range(max_spots):
                new_spot=ParkingSpot(lot_id=new_pkl.id)
                new_spot.price=pph
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
        return render_template("reserve_lot.html", lot_id=lot_id, user_id=user_id, spot=first_av_spot, pklot=pklot)
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
        pkspots=pklot.pkspots
        for spot in pkspots:
            reservations=Reserve.query.filter_by(spot_id=spot.id).all()
            for reservation in reservations:
                db.session.delete(reservation)
            db.session.delete(spot)
        db.session.delete(pklot)
        db.session.commit()
    else:
        return render_template("spot_occ.html")
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
            new_price=request.form.get("price")
            #updates the price of all available spots in the lot at once
            spots=ParkingSpot.query.filter_by(lot_id=lot_id)
            for spot in spots:
                #slot price can be changed only if it is available
                if spot.status=="Available":
                    spot.price=new_price
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
        
@app.route("/release_spot/<int:res_id>/<int:spot_id>")
def release_spot(res_id, spot_id):
    reservation=Reserve.query.get(res_id)
    spot=ParkingSpot.query.get(spot_id)
    lot_id=spot.lot_id
    lot=ParkingLot.query.get(lot_id)
    if spot.status=="Booked":
        reservation.leaving_timestamp=datetime.now()
        # Calculate duration
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        total_minutes = duration.total_seconds() / 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)

        # Get price per hour
        price_per_hour = spot.price

        # Calculate cost
        if hours == 0:
            cost = price_per_hour
        elif minutes < 30:
            cost = hours * price_per_hour
        else:
            cost = (hours + 1) * price_per_hour

        reservation.parking_cost=cost
        spot.status="Available"
        lot.occ_spots=lot.occ_spots-1
        lot.revenue_generated=lot.revenue_generated+cost

        db.session.commit()
    else:
        cost=reservation.parking_cost

    return render_template("release_lot.html", reservation=reservation, spot=spot, lot=lot, cost=cost)
@app.route("/spot_controls/<int:spot_id>")
def spot_control(spot_id):
    spot=ParkingSpot.query.filter_by(id=spot_id).first()
    if spot.status == "Booked":
        reservation = Reserve.query.filter(
               Reserve.leaving_timestamp.is_(None),
               Reserve.spot_id == spot.id
               ).first()
        user=User.query.filter_by(id=reservation.user_id).first()
        return render_template("booked_spot_details.html", spot=spot, reservation=reservation, user=user)
    else:
        return render_template("av_spot_controls.html", spot=spot)

@app.route("/avspot_actions/<int:spot_id>", methods=["POST"])
def avspot_actions(spot_id):
    action=request.form.get('action')
    if action=="BACK":
        return redirect(url_for('admin_dashboard'))
    if action=="UPDATE PRICE":
        spot=ParkingSpot.query.filter_by(id=spot_id).first()
        new_price=request.form.get('price')
        spot.price=new_price
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    if action=="DELETE SPOT":
        spot=ParkingSpot.query.filter_by(id=spot_id).first()
        reservations=Reserve.query.filter_by(spot_id=spot_id).all()
        if spot:
            for reservation in reservations:
                db.session.delete(reservation)
            db.session.delete(spot)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
            
@app.route('/lot_summary')
def lot_summary():
    #pie chart on status of parking spots
    occ=len(ParkingSpot.query.filter_by(status="Booked").all())
    av=len(ParkingSpot.query.filter_by(status="Available").all())
    if occ==0 and av==0:
        return render_template("no_data.html")
    labels=["Booked","Available"]
    sizes=[occ,av]
    colors=["red", "green"]
    plt.pie(sizes,labels=labels,colors=colors,autopct="%1.1f%%")
    plt.title("Status of Parking Spots")
    plt.savefig("static/pie.png")
    plt.clf()

    #bar graph on revnue generated by parking lots
    pklots=ParkingLot.query.all()
    labels=[pklot.id for pklot in pklots]
    sizes=[pklot.revenue_generated for pklot in pklots]
    bars=plt.bar(labels,sizes)
    plt.title("Revenue Generated by Parking Lots")
    plt.xlabel("Parking Lots -->")
    plt.ylabel("Revenue Generated(in Rs.) -->")
    # Force integer x-axis labels
    plt.xticks(labels)
    # Show values on top of bars
    plt.bar_label(bars, padding=2)
    plt.savefig("static/bar.png")
    plt.clf()
    return render_template("summary.html")