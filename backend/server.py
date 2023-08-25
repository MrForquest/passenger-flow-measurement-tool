from flask import Flask, request, jsonify
from flask_cors import CORS
from data import stations
from models.traffic_predictor import TrafficPredictor
import datetime

application = Flask(__name__)
cors = CORS(application)

application.config['SECRET_KEY'] = 'werty57i39fj92udifkdb56fwed232z'
model = TrafficPredictor()


@application.route("/stations/", methods=['GET'])
def get_stations():
    date = request.args.get("date")
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    hour = int(request.args.get("hour"))

    response = list()

    for st_id, st_info in stations.items():
        prediction = model.predict_traffic_date(
            date=date,
            hour=hour,
            line=st_info[0],
            station=st_info[1], )
        response.append(
            {"id": st_id,
             "loadedPercentage": round((prediction / st_info[2]) * 100)}
        )
    return jsonify(response)


@application.route("/stations/<station_id>/", methods=['GET'])
def get_station_detail(station_id):
    station_id = int(station_id)
    date = request.args.get("date")
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    hour = int(request.args.get("hour"))
    'date', 'line', 'station'

    prediction = model.predict_traffic_date(
        date=date,
        hour=hour,
        line=stations[station_id][0],
        station=stations[station_id][1], )

    name = stations[station_id][1]
    loaded_percentage = round((prediction / stations[station_id][2]) * 100)
    commentaries = []
    graphic_info = model.predict_traffic_day(
        date=date,
        line=stations[station_id][0],
        station=stations[station_id][1],
    )
    return jsonify({"id": station_id,
                    "name": name,
                    "loadedPercentage": loaded_percentage,
                    "commentaries": commentaries,
                    "graphicInfo": graphic_info})


def main():
    application.run(port=5000)


if __name__ == '__main__':
    main()
