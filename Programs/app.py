# Import flask
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, MetaData

import numpy as np
import datetime as dt

# ********************************************************************************************************************************************
# Database setup
# ********************************************************************************************************************************************

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# # Declare a Base using 'automap_base()'
Base = automap_base()

# #Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a temp and date dictionary

# Create our session (link) from Python to the DB
session = Session(engine)
    
"""Return a dictionary with date and temperature value"""
temp_obs = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.asc()).all()
session.close()
    
temperature = []
for date, tobs in temp_obs:
    temp_dic = {}
    temp_dic['date'] = date
    temp_dic['tobs'] = tobs
    temperature.append(temp_dic)

# ********************************************************************************************************************************************
# Flask setup
# ********************************************************************************************************************************************
app = Flask(__name__)

# Flask routes

# Defines what to do when a use hits a the index route
@app.route("/")
def home():
    return(
    f"Welcome to the Hawaii API. Here is the list of all available routes:</br></br>"
    f"/api/v1.0/precipitation;</br>"
    f"/api/v1.0/stations;</br>"
    f"/api/v1.0/tobs;</br>"
    f"/api/v1.0/'start';</br>"    
    f"/api/v1.0/'start'/'end'" 
    )


@app.route("/api/v1.0/precipitation")
def prec():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a dictionary with date and precipitation value"""
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    session.close()
    
    precipitation = []
    for date, prcp in results:
        precipt_dic = {}
        precipt_dic['date'] = date
        precipt_dic['prcp'] = prcp
        precipitation.append(precipt_dic)
    return jsonify(precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a JSON list of stations from the dataset"""
    list_station=session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    
    return jsonify(list_station)
    

@app.route("/api/v1.0/tobs")
def tobs_station():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query stations and select the most active station
    list_station=session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    first_station=list_station[0][0]

    # Query the dates and temperature observations of the most active station for the last year of data
    station_begin_date = session.query(Measurement.date).filter(Measurement.station == first_station).\
    order_by(Measurement.date.desc()).first().date

    last_12_months_station = dt.datetime.strptime(station_begin_date, '%Y-%m-%d') - dt.timedelta(days=365)
    m = last_12_months_station.strftime("%m")
    y = last_12_months_station.strftime("%Y")
    d = last_12_months_station.strftime("%d")
    last_12_months_station = str(y+'-'+m+'-'+d)


    station = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == first_station).\
    filter(Measurement.date >= last_12_months_station).all()
    session.close()
    
    return jsonify(station)


@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    def calc_temps(start):
  
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    
 
    begin_date = dt.datetime.strptime(start, '%Y-%m-%d')
    
    if begin_date>=  dt.datetime.strptime("2010-1-1", '%Y-%m-%d') and begin_date<=  dt.datetime.strptime("2017-8-23", '%Y-%m-%d'): 
        temp_data = (calc_temps(start))
        temp_stats = []
        tobs_dic = {}
        tobs_dic['min temp'] = temp_data[0][0]
        tobs_dic['avg temp'] = temp_data[0][1]
        tobs_dic['max temp'] = temp_data[0][2]
        temp_stats.append(tobs_dic)
        return jsonify(temp_stats)
    return jsonify({"error": f"Date {start} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    def calc_temps(start,end):
  
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    
    begin_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

        
    if begin_date<=end_date and begin_date>= dt.datetime.strptime("2010-1-1", '%Y-%m-%d') and end_date<=  dt.datetime.strptime("2017-8-23", '%Y-%m-%d'): 
    
        temp_data = (calc_temps(start,end))
        temp_stats = []
        tobs_dic = {}
        tobs_dic['min temp'] = temp_data[0][0]
        tobs_dic['avg temp'] = temp_data[0][1]
        tobs_dic['max temp'] = temp_data[0][2]
        temp_stats.append(tobs_dic)
        return jsonify(temp_stats)
    return jsonify({"error": f"Either date {start} or date {end} not found, or start date greater than end date."}), 404


if __name__ == '__main__':
    app.run(debug=True)