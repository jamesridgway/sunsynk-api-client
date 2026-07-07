from sunsynk.resource import Resource


class Weather(Resource):
    def __init__(self, data):
        curr_wea = data.get('currWea') or {}
        self.description = curr_wea.get('desc')
        self.current_temp = curr_wea.get('currTemp')
        self.wind_speed = curr_wea.get('windSpeed')
        self.wind_direction = curr_wea.get('windDirection')
        self.sunrise = curr_wea.get('sunrise')
        self.sunset = curr_wea.get('sunset')
        self.icon_url = curr_wea.get('iconUrl')
        self.temp_min_c = curr_wea.get('tempMinC')
        self.temp_max_c = curr_wea.get('tempMaxC')

    def get_current_temp(self) -> float | None:
        if self.current_temp is None:
            return None
        return float(self.current_temp)

    def get_wind_speed(self) -> float | None:
        if self.wind_speed is None:
            return None
        return float(self.wind_speed)

    def get_wind_direction(self) -> int | None:
        if self.wind_direction is None:
            return None
        return int(self.wind_direction)

    def get_temp_min_c(self) -> float | None:
        if self.temp_min_c is None:
            return None
        return float(self.temp_min_c)

    def get_temp_max_c(self) -> float | None:
        if self.temp_max_c is None:
            return None
        return float(self.temp_max_c)
