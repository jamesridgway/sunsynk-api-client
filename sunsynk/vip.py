from sunsynk.resource import Resource


class Vip(Resource):
    def __init__(self, data):
        self.voltage = data['volt']
        self.current = data['current']
        self.power = data['power']
