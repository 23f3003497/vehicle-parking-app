from flask import Flask, render_template, redirect, request
from flask import current_app as app #directly importing app-> circular import error, current_app is the app object created in app.py
from .models import User, ParkingLot, ParkingSpot, Reserve
