import asyncio
import os

import nest_asyncio
from isdayoff import ProdCalendar
import joblib
import datetime
from catboost import CatBoostRegressor
from sklearn.preprocessing import LabelEncoder

nest_asyncio.apply()
DIR = os.path.dirname(__file__)


class TrafficPredictor:
    def __init__(self, model_path=None, le_line_path=None,
                 le_station_path=None):
        if model_path is None:
            model_path = os.path.join(DIR, "catboost_model_best_201.cbm")
        if le_line_path is None:
            le_line_path = os.path.join(DIR, "label_encoder_line.joblib")
        if le_station_path is None:
            le_station_path = os.path.join(DIR, "label_encoder_station.joblib")
        self.weights = model_path
        self.le_line = joblib.load(le_line_path)
        self.le_station = joblib.load(le_station_path)
        self.model = CatBoostRegressor()
        self.model.load_model(self.weights)
        self.calendar = ProdCalendar(locale="ru")
        self.is_dayoff_cache = asyncio.run(
            self.calendar.range_date(datetime.date(2023, 1, 1),
                                     datetime.date(2024, 1, 1)),
        )

    def get_weekday(self, x):
        x = x.date().weekday()
        return x + 1

    def is_holiday(self, x):
        res = self.is_dayoff_cache.get(
            x.strftime("%Y.%m.%d"),
            None,
        )
        if res is None:
            res = asyncio.run(self.calendar.date(x))

        if res == 4:
            return 0
        return int(res == 1)

    def get_season(self, x):
        x = x.date()
        if x.month in (12, 1, 2):
            return 1
        if x.month in (3, 4, 5):
            return 2
        if x.month in (6, 7, 8):
            return 3
        if x.month in (9, 10, 11):
            return 4

    def get_year(self, x):
        return x.date().year

    def get_month(self, x):
        return x.date().month

    def get_day(self, x):
        return x.date().day

    def predict_traffic_date(self, date, hour, line, station):
        station_encode = self.le_station.fit_transform([station]).item()
        line_encode = self.le_line.fit_transform([line]).item()
        weekday = self.get_weekday(date)
        is_holiday = self.is_holiday(date)
        season = self.get_season(date)
        month = self.get_month(date)
        day = self.get_day(date)
        model_input = [
            station_encode,
            line_encode,
            hour,
            weekday,
            is_holiday,
            season,
            month,
            day,
        ]

        self.output = self.model.predict(model_input)

        return int(max(self.output, 0))

    def predict_traffic_day(self, date, line, station):
        predict_all_day = list()
        for hour in range(5, 24):
            num_val = int(self.predict_traffic_date(date, hour, line, station))
            predict_all_day.append((hour, num_val))
        return predict_all_day
