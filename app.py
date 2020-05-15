import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import Flask, jsonify
import datetime as dt

#setting up database
#creating the engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflecting an existing db in a new modal
Base = automap_base()
#reflecting the tables
Base.prepare(engine, reflect=True)

#saving reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#creating a session link from Python
session = Session(engine)

#setting up Flask
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    """Listing all available api routes"""
    return(
        f"Availabile Routes: <br>"
        f"/api/v1.0/precipitation <br>"
        f"/api/v1.0/stations <br>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def prcpp():
    #querying the percipitation
    latest_yr = session.query(Measurement.date).order_by(Measurement.date)
    latest_yr = latest_yr [0]
    oneyear_ago = dt.datetime.strptime(latest_yr, "%Y-%m-%d")- dt.timedelta(days=366)
    querydate=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>= oneyear_ago)
    
    #returnig the dict in a jsonified format
    prcp_result = dict(latest_yr)
    return jsonify(prcp_result)


@app.route("/api/v1.0/stations")
def stat():
    #querying the stations
    station_query = session.query(Measurement.station).group_by(Measurement.station).all()
    station_results = list(station_query)
    #returnig the list in a jsonified formart
    return jsonify(station_results)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    active_stations = session.query(Station.station, Station.name).all()
    return jsonify(active_stations)


# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    temp_results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= last_twelve_months).all()
    return jsonify(temp_results)


# /api/v1.0/<start>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<date>")
def startDateOnly(date):
    daytemp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    return jsonify(daytemp_results)


# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    multi_daytemp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(multi_daytemp_results)

if __name__ == "__main__":
    app.run(debug=True)
