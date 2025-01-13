# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

Base.prepare(autoload_with=engine)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
        f"/api/v1.0/<start>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Output the prcp data from last 12 months"""
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    results1 = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    session.close()

    prcp_data = []
    for date, prcp in results1:
        prcp_data.append({"date": date, "precipitation": prcp})

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    """List of stations from the dataset"""
    results2 = session.query(station.station).all()

    session.close()

    stations = []
    for station in results2:
        stations.append({"station": station})

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature observations for the previous year"""
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    active_stations = session.query(measurement.station,func.count(measurement.id).label('count')).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()
    most_active_station_id = active_stations[0][0]
    results3 = session.query(measurement.tobs).filter(measurement.station == most_active_station_id,measurement.date >= one_year_ago).all()

    session.close()

    tobs = []
    for i in results3:
        tobs.append({"station": most_active_station_id,'tobs':i[0]})

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end=None):
    """minimum temperature, the average temperature, and the maximum temperature"""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    if end:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    else:
        end_date = dt.date.today()
     
    results3 = session.query(
    func.min(measurement.tobs).label("min_temp"),
    func.max(measurement.tobs).label("max_temp"),
    func.avg(measurement.tobs).label("avg_temp")
    ).filter(measurement.date == start_date).filter(measurement.date <= end_date).all()

    session.close()

    temp_stats = []
    for result in results3:
        temp_stats.append({
            "min_temp": result.min_temp,
            "max_temp": result.max_temp,
            "avg_temp": result.avg_temp
        })


    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)