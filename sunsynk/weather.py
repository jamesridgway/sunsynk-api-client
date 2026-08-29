from typing import Any

from sunsynk.resource import Resource, to_float, to_int


class Weather(Resource):
    """Current weather at a plant's location."""

    def __init__(self, data: dict[str, Any]):
        curr_wea = data.get('currWea') or {}
        self.description = curr_wea.get('desc')
        self.current_temp = to_float(curr_wea.get('currTemp'))
        self.wind_speed = to_float(curr_wea.get('windSpeed'))
        self.wind_direction = to_int(curr_wea.get('windDirection'))
        self.sunrise = curr_wea.get('sunrise')
        self.sunset = curr_wea.get('sunset')
        self.icon_url = curr_wea.get('iconUrl')
        self.temp_min_c = to_float(curr_wea.get('tempMinC'))
        self.temp_max_c = to_float(curr_wea.get('tempMaxC'))

    def get_current_temp(self) -> float | None:
        return self.current_temp

    def get_wind_speed(self) -> float | None:
        return self.wind_speed

    def get_wind_direction(self) -> int | None:
        return self.wind_direction

    def get_temp_min_c(self) -> float | None:
        return self.temp_min_c

    def get_temp_max_c(self) -> float | None:
        return self.temp_max_c
