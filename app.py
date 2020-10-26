import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes["measurement"]
Station = Base.classes["station"]
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
        f"/api/v1.0/start/end<br/>"
        # f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def names():
      

    #Return a dictionary with the dates and the precipitation
    lastest_date = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(lastest_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    measurement_cols = (Measurement.date, Measurement.prcp)
    prcp_data = session.query(*measurement_cols).\
        filter(Measurement.date >= last_year_date).all()

    
    precipt_dict = {}
    for date, precipitation in prcp_data:
        precipt_dict[date] = precipitation
       
    return jsonify(precipt_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    count_by_station =  session.query(Measurement.station).all()
    stations=list(np.ravel(count_by_station)    )
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').all()
    tobs=list(np.ravel(tobs)    )
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    #Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than 
        # and equal to the start date.
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    # for dates between the start and end date inclusive.
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)




if __name__ == '__main__':
    app.run(debug=True)
