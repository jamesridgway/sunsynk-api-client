import json

from aiohttp import web

from sunsynk.client import SunsynkClient


class MockApiServer:
    def __init__(self, aiohttp_client):
        self.aiohttp_client = aiohttp_client
        self.app = web.Application()
        self.app.router.add_post('/oauth/token', self.login)
        self.app.router.add_get('/api/v1/inverters', self.get_inverters)
        self.app.router.add_get('/api/v1/plants', self.get_plants)
        self.app.router.add_get('/api/v1/inverter/grid/1029384756/realtime', self.get_inverter_realtime_grid)
        self.app.router.add_get('/api/v1/inverter/battery/1029384756/realtime', self.get_inverter_realtime_battery)
        self.app.router.add_get('/api/v1/inverter/1029384756/realtime/input', self.get_inverter_realtime_input)
        self.app.router.add_get('/api/v1/inverter/1029384756/realtime/output', self.get_inverter_realtime_output)

    async def client(self):
        client = await self.aiohttp_client(self.app)
        return await SunsynkClient.create('myuser', 'letmein', base_url=f'http://{client.host}:{client.port}')

    async def login(self, request):
        payload = {
            'data': {
                'access_token': 'AT123',
                'refresh_token': 'RT456'
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_inverters(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "pageSize": 10,
                "pageNumber": 1,
                "total": 1,
                "infos": [
                    {
                        "sn": "1029384756",
                        "alias": "1029384756",
                        "gsn": "E0192837465",
                        "status": 1,
                        "type": 2,
                        "commTypeName": "RS485",
                        "custCode": 29,
                        "version": {
                            "masterVer": "2.3.7.4",
                            "softVer": "1.5.1.5",
                            "hardVer": "",
                            "hmiVer": "E.4.2.4",
                            "bmsVer": ""
                        },
                        "model": "",
                        "equipMode": None,
                        "pac": 61,
                        "etoday": 1.7,
                        "etotal": 375.1,
                        "updateAt": "2023-01-07T15:40:02Z", "opened": 1,
                        "plant": {
                            "id": 12345,
                            "name": "John Smith",
                            "type": 2,
                            "master": None,
                            "installer": None,
                            "email": None,
                            "phone": None
                        },
                        "gatewayVO": {
                            "gsn": "E0192837465",
                            "status": 2
                        },
                        "sunsynkEquip": True,
                        "protocolIdentifier": "2"
                    }
                ]
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_plants(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "pageSize": 10,
                "pageNumber": 1,
                "total": 1,
                "infos": [
                    {
                        "id": 12345,
                        "name": "John Smith",
                        "thumbUrl": "https://",
                        "status": 1,
                        "address": "123 Fake Street",
                        "pac": 38,
                        "efficiency": 0.011,
                        "etoday": 1.7,
                        "etotal": 370.5,
                        "updateAt": "2023-01-07T15:55:06Z",
                        "createAt": "2022-10-03T15:39:21.000+00:00",
                        "type": 2,
                        "masterId": 54321,
                        "share": False,
                        "plantPermission": [
                            "station.share.cancle"
                        ],
                        "existCamera": False
                    }
                ]
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_inverter_realtime_grid(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "vip":
                    [
                        {"volt": "233.6",
                         "current": "0.8",
                         "power": 610
                         }
                    ],
                "pac": 610,
                "qac": 0,
                "fac": 50.08,
                "pf": 1.0,
                "status": 1,
                "etodayFrom": "12.2",
                "etodayTo": "0.0",
                "etotalFrom": "998.5",
                "etotalTo": "48.2",
                "limiterPowerArr": [610, 0],
                "limiterTotalPower": 610
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_inverter_realtime_battery(self, request):
        payload = {
            'code': 0,
            'msg': 'Success',
            'data': {
                'time': None,
                'etodayChg': '1.1',
                'etodayDischg': '0.6',
                'emonthChg': '7.5',
                'emonthDischg': '6.2',
                'eyearChg': '7.5',
                'eyearDischg': '6.2',
                'etotalChg': '188.5',
                'etotalDischg': '147.9',
                'type': 1,
                'power': -18,
                'capacity': '100.0',
                'correctCap': 100,
                'current': '-0.4',
                'voltage': '53.3',
                'temp': '18.7',
                'soc': '20.0',
                'chargeVolt': 56.1,
                'dischargeVolt': 0.0,
                'chargeCurrentLimit': 50.0,
                'dischargeCurrentLimit': 50.0,
                'maxChargeCurrentLimit': 0.0,
                'maxDischargeCurrentLimit': 0.0,
                'current2': None,
                'voltage2': None,
                'temp2': None,
                'soc2': None,
                'chargeVolt2': None,
                'dischargeVolt2': None,
                'chargeCurrentLimit2': None,
                'dischargeCurrentLimit2': None,
                'maxChargeCurrentLimit2': None,
                'maxDischargeCurrentLimit2': None,
                'status': 1,
                'batterySoc1': 0.0,
                'batteryCurrent1': 0.0,
                'batteryVolt1': 0.0,
                'batteryPower1': 0.0,
                'batteryTemp1': 0.0,
                'batteryStatus2': 0,
                'batterySoc2': None,
                'batteryCurrent2': None,
                'batteryVolt2': None,
                'batteryPower2': None,
                'batteryTemp2': None,
                'numberOfBatteries': None,
                'batt1Factory': None,
                'batt2Factory': None
            },
            'success': True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_inverter_realtime_input(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "pac": 9, "pvIV":
                    [
                        {
                            "id": None,
                            "pvNo": 1,
                            "vpv": "91.5",
                            "ipv": "0.1",
                            "ppv": "9.0",
                            "todayPv": "0.0",
                            "sn": "1029384756",
                            "time": "2023-01-07 16:50:17"
                        },
                        {
                            "id": None,
                            "pvNo": 2,
                            "vpv": "2.4",
                            "ipv": "0.1",
                            "ppv": "0.0",
                            "todayPv": "0.0",
                            "sn": "1029384756",
                            "time": "2023-01-07 16:50:17"
                        }
                    ],
                "mpptIV": [],
                "etoday": 1.8,
                "etotal": 375.2
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_inverter_realtime_output(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "vip":
                    [
                        {
                            "volt": "230.8",
                            "current": "0.3",
                            "power": -50
                        }
                    ],
                "pInv": 9,
                "pac": -50,
                "fac": 50.0
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)


