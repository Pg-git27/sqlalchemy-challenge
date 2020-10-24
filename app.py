#Import dependencies

from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///Resources/hawaii.sqlite'

db= SQLAlchemy(app)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session =  Session(engine)
#List all the routes

app = Flask(__name__)
@app.route('/')
def home():
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
)

#Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
   results = session.query(Station.name).all()
   all_stations = list(np.ravel(results))

   return jsonify(all_stations)
# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement).all()
    session.close()

    year_prcp = []
    for result in results:
            year_prcp_dict = {}
            year_prcp_dict["date"] = result.date
            year_prcp_dict["prcp"] = result.prcp
            year_prcp.append(year_prcp_dict)
  #return the JSON representation of your dictionary
    return jsonify(year_prcp)
#Query the dates and temp. observations of the most active station for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_results = session.query(Measurement.station, Measurement.tobs).filter(Measurement.date.between('2016-08-01', '2017-08-01')).all()

    tobs_list=[]
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["station"] = tobs[0]
        tobs_dict["tobs"] = float(tobs[1])

        tobs_list.append(tobs_dict)
#return a JSON list of temp. observs for the previous year
    return jsonify(tobs_list)
#Return a JSON list of the minimum temp. , avg temp and the max temp. for a given start range
@app.route("/api/v1.0/<start>")
def start_day(start='start_date'):
    start_date = datetime.strptime('2016-08-01', '%Y-%m-%d').date()
    start_results = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)
   
    start_tobs = []
    for tobs in start_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_tobs.append(tobs_dict)
    
    return jsonify(start_tobs)
#Given the start and the end date , calculate the TMIN, TAVG,TMAX for all the dates between the start and end date
@app.route("/api/v1.0/calc_temps/<start>/<end>")
def calc_temp(start='start_date', end='end_date'):
    start_date = datetime.strptime('2016-08-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2017-08-01', '%Y-%m-%d').date()

    start_end_results= session.query(func.max(Measurement.tobs).label("max_tobs"), func.min(Measurement.tobs).label("min_tobs"), func.avg(Measurement.tobs).label("avg_tobs")).filter(Measurement.date.between(start_date, end_date))
    start_end_tobs =[]

    for tobs in start_end_results:
        tobs_dict ={}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_end_tobs.append(tobs_dict)
    return jsonify(start_end_tobs)
     
if __name__ == "__main__":
    app.run(debug= True)
