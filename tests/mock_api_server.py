import base64
import json

from aiohttp import web
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from sunsynk.client import SunsynkClient


class MockApiServer:
    def __init__(self, aiohttp_client):
        self.aiohttp_client = aiohttp_client
        self._private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_der = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self._public_key_b64 = base64.b64encode(public_der).decode()
        self.battery_connected = True
        self.app = web.Application()
        self.app.router.add_get('/anonymous/publicKey', self.get_public_key)
        self.app.router.add_post('/oauth/token/new', self.login)
        self.app.router.add_get('/api/v1/inverters', self.get_inverters)
        self.app.router.add_get('/api/v1/plants', self.get_plants)
        self.app.router.add_get('/api/v1/inverter/grid/1029384756/realtime', self.get_inverter_realtime_grid)
        self.app.router.add_get('/api/v1/inverter/battery/1029384756/realtime', self.get_inverter_realtime_battery)
        self.app.router.add_get('/api/v1/inverter/1029384756/realtime/input', self.get_inverter_realtime_input)
        self.app.router.add_get('/api/v1/inverter/1029384756/realtime/output', self.get_inverter_realtime_output)
        self.app.router.add_get('/api/v1/inverter/load/1029384756/realtime', self.get_inverter_realtime_load)
        self.app.router.add_get('/api/v1/plant/12345', self.get_plant)
        self.app.router.add_get('/api/v1/weather', self.get_weather)
        self.app.router.add_get('/api/v1/user', self.get_user)
        self.app.router.add_get('/api/v1/inverter/1029384756', self.get_inverter)
        self.app.router.add_get('/api/v1/inverter/1029384756/flow', self.get_inverter_flow)
        self.app.router.add_get('/api/v1/inverter/1029384756/output/day', self.get_inverter_output_day)
        self.app.router.add_get('/api/v1/common/setting/1029384756/read', self.get_inverter_settings)
        self.app.router.add_post('/api/v1/common/setting/1029384756/set', self.set_inverter_settings)
        self.app.router.add_get('/api/v1/plant/12345/realtime', self.get_plant_realtime)
        self.app.router.add_get('/api/v1/plant/energy/12345/day', self.get_plant_energy_day)
        self.app.router.add_get('/api/v1/plant/energy/12345/month', self.get_plant_energy_month)
        self.app.router.add_post('/api/v1/plant/12345/income', self.set_plant_income)
        self.requests = []
        self.settings_writes = []
        self.income_writes = []
        self.app.middlewares.append(self._record_requests)

    async def client(self, username='myuser'):
        client = await self.aiohttp_client(self.app)
        return await SunsynkClient.create(username, 'letmein', base_url=f'http://{client.host}:{client.port}')

    async def get_public_key(self, request):
        payload = {
            'code': 0,
            'msg': 'Success',
            'data': self._public_key_b64,
            'success': True,
        }
        return web.Response(text=json.dumps(payload),
                            headers={'Content-Type': 'application/json'})

    async def login(self, request):
        request_body = await request.json()
        try:
            ciphertext = base64.b64decode(request_body['password'])
            decrypted = self._private_key.decrypt(ciphertext, padding.PKCS1v15()).decode()
        except Exception:
            decrypted = None
        success = request_body['username'] == 'myuser' and decrypted == 'letmein'
        payload = {
            'success': success,
            'data': {
                'access_token': 'AT123',
                'refresh_token': 'RT456',
                'expires_in': 3600,
                'token_type': 'bearer',
                'scope': 'all'
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
        if not self.battery_connected:
            return await self.get_inverter_realtime_battery_absent(request)
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

    async def get_inverter_realtime_battery_absent(self, request):
        payload = {
            'code': 0,
            'msg': 'Success',
            'data': {
                'time': None,
                'etodayChg': '0.0',
                'etodayDischg': '0.0',
                'emonthChg': '0.0',
                'emonthDischg': '0.0',
                'eyearChg': '0.0',
                'eyearDischg': '0.0',
                'etotalChg': '0.0',
                'etotalDischg': '0.0',
                'type': 0,
                'power': 0,
                'capacity': '0.0',
                'correctCap': 0,
                'current': '0.0',
                'voltage': '0.0',
                'temp': '0.0',
                'soc': '0.0',
                'chargeVolt': 0.0,
                'dischargeVolt': 0.0,
                'chargeCurrentLimit': 0.0,
                'dischargeCurrentLimit': 0.0,
                'maxChargeCurrentLimit': 0.0,
                'maxDischargeCurrentLimit': 0.0,
                'status': 0,
                'batterySoc1': None,
                'batteryCurrent1': None,
                'batteryVolt1': None,
                'batteryPower1': None,
                'batteryTemp1': None,
                'batteryStatus2': None,
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
        return web.Response(text=json.dumps(payload), headers={'Content-Type': 'application/json'})

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

    async def get_inverter_realtime_load(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "totalUsed": 3133.10,
                "dailyUsed": 34.70,
                "vip": [
                    {
                        "volt": "246.6",
                        "current": "0.0",
                        "power": 3427
                    }
                ],
                "totalPower": 3427,
                "smartLoadStatus": -1,
                "loadFac": 50.01,
                "upsPowerL1": 5.0,
                "upsPowerL2": 0.0,
                "upsPowerL3": 0.0,
                "upsPowerTotal": 5.0
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_plant(self, request):
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "id": 12345,
                "name": "John Smith",
                "totalPower": 3.68,
                "thumbUrl": "https://",
                "joinDate": "2025-02-20T00:00:00Z",
                "type": 2,
                "status": 1,
                "charges": [
                    {
                        "id": 112001545,
                        "startRange": "00:00",
                        "endRange": "24:00",
                        "price": 0.15,
                        "type": 1,
                        "stationId": 12345,
                        "createAt": "2026-03-30T13:13:36Z",
                        "status": None
                    }
                ],
                "products": None,
                "lon": -0.724613,
                "lat": 51.322984,
                "address": "123 Fake Street",
                "master": {
                    "id": 54321,
                    "nickname": "master@gmail.com",
                    "mobile": None
                },
                "currency": {
                    "id": 366,
                    "code": "GBP",
                    "text": "£"
                },
                "timezone": {
                    "id": 234,
                    "code": "Europe/London",
                    "text": "(UTC+00:00)Dublin,Edinburgh,Lisbon,London"
                },
                "realtime": {
                    "pac": 2484,
                    "efficiency": 0.000,
                    "etoday": 9.00,
                    "emonth": 119.40,
                    "eyear": 1776.50,
                    "etotal": 5622.30,
                    "totalPower": 3.68,
                    "currency": {
                        "id": 366,
                        "code": "GBP",
                        "text": "£"
                    },
                    "invest": 8320.00,
                    "income": 1.3500,
                    "updateAt": "2026-07-07T12:02:52Z"
                },
                "createAt": "2022-10-03T15:39:21.000+00:00",
                "phone": "01257443377",
                "email": "",
                "installer": "",
                "principal": "Contact Solar",
                "plantPermission": [
                    "station.share.cancle"
                ],
                "fluxProducts": None,
                "productWarrantyRegistered": 0,
                "ctEnable": 1,
                "invest": 8320.00,
                "epexProduct": None
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    async def get_user(self, request):
        assert request.query.get('lan') == 'en'
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "id": 281092,
                "nickname": "john.smith@example.com",
                "avatar": "https://sunsynk-s3.s3.eu-west-2.amazonaws.com/avatar/20210126155052363929.png",
                "gender": 1,
                "mobile": None,
                "createAt": "2022-10-03T15:39:04Z",
                "type": None,
                "tempUnit": "\u2103",
                "company": None,
                "userSrc": "sunsynk",
                "email": "john.smith@example.com",
                "sex": 1
            },
            "success": True
        }
        return web.Response(text=json.dumps(payload), headers={'Content-Type': 'application/json'})

    async def get_weather(self, request):
        lon_lat = request.query.get('lonLat')
        assert lon_lat == '51.322984,-0.724613'
        payload = {
            "code": 0,
            "msg": "Success",
            "data": {
                "currWea": {
                    "desc": "broken clouds",
                    "currTemp": "20.6",
                    "windSpeed": "3.9",
                    "windDirection": "292",
                    "sunrise": "04:55",
                    "sunset": "21:19",
                    "iconUrl": "https://sunsynk-s3.s3.eu-west-2.amazonaws.com/weather/openweather/04d.png",
                    "tempMinC": "19.7",
                    "tempMaxC": "21.8"
                }
            },
            "success": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        return web.Response(text=json.dumps(payload), headers=headers)

    @web.middleware
    async def _record_requests(self, request, handler):
        self.requests.append((request.method, request.path, dict(request.query)))
        return await handler(request)

    @staticmethod
    def _json(payload):
        return web.Response(text=json.dumps(payload), headers={'Content-Type': 'application/json'})

    async def get_inverter(self, request):
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {
                "id": 1, "sn": "1029384756", "alias": "My Inverter", "gsn": "E0192837465",
                "status": 1, "runStatus": 1, "type": 2, "commType": 1, "commTypeName": "RS485",
                "custCode": 29, "thumbUrl": "", "opened": 1,
                "version": {"masterVer": "1234", "softVer": "1.2.3.4", "hardVer": "1.0",
                            "hmiVer": "E.1.2.3", "bmsVer": "1.0", "commVer": "1.0"},
                "plant": {"id": 12345, "name": "John Smith", "type": 2, "master": None,
                          "installer": None, "email": "john.smith@example.com", "phone": None},
                "pac": 2484, "etoday": 9.0, "emonth": 120.5, "eyear": 1500.25, "etotal": 5622.3,
                "updateAt": "2023-01-07T16:50:17Z", "ratePower": 5000.0, "brand": "Sunsynk",
                "address": "Somewhere", "model": "SUNSYNK-5K-SG04LP1", "protocolIdentifier": "2",
                "equipType": 2, "equipMode": 2, "sunsynkEquip": True,
                "user": {"id": 281092, "nickname": "john", "mobile": None, "email": "john.smith@example.com"},
            },
        })

    async def get_inverter_flow(self, request):
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {
                "custCode": 29, "meterCode": 0, "protocolIdentifier": "2",
                "pvPower": 9, "battPower": -18, "battPower2": None, "gridOrMeterPower": 610,
                "loadOrEpsPower": 3427, "genPower": 0, "minPower": 0, "soc": 20.0,
                "heatPumpPower": None, "smartLoadPower": None, "upsLoadPower": 5, "homeLoadPower": 3422,
                "pvTo": True, "toLoad": True, "toGrid": False, "toBat": False, "batTo": True,
                "gridTo": True, "genTo": False, "minTo": False, "existsGen": False, "existsMin": False,
                "genOn": False, "microOn": False, "existsMeter": False, "bmsCommFaultFlag": False,
                "existThinkPower": False,
            },
        })

    async def get_inverter_output_day(self, request):
        assert request.query.get('date') == '2026-07-07'
        columns = request.query.get('column', '').split(',')
        infos = []
        if 'dc_temp' in columns:
            infos.append({"unit": "℃", "records": [
                {"time": "2026-07-07 10:00:00", "value": "40.1", "updateTime": None},
                {"time": "2026-07-07 10:05:00", "value": "41.3", "updateTime": None}],
                "id": None, "label": "DC Temp"})
        if 'igbt_temp' in columns:
            infos.append({"unit": "℃", "records": [
                {"time": "2026-07-07 10:00:00", "value": "35.0", "updateTime": None},
                {"time": "2026-07-07 10:05:00", "value": "36.5", "updateTime": None}],
                "id": None, "label": "AC Temp"})
        if 'pac' in columns:
            infos.append({"unit": "W", "records": [
                {"time": "2026-07-07 10:00:00", "value": "1200", "updateTime": None}],
                "id": None, "label": "pac"})
        return self._json({"code": 0, "msg": "Success", "success": True, "data": {"infos": infos}})

    async def get_inverter_settings(self, request):
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {
                "sn": "1029384756", "energyMode": "1", "sysWorkMode": "2", "workState": "1",
                "batteryLowCap": "20", "batteryShutdownCap": "10", "batteryRestartCap": "15",
                "batteryCap": "100", "batteryMaxCurrentCharge": "80", "batteryMaxCurrentDischarge": "80",
                "zeroExportPower": "20", "solarSell": "1", "solarMaxSellPower": "5000",
                "peakAndVallery": 1, "genChargeOn": "0", "gridPeakShaving": "0", "gridPeakPower": "8000",
                "battType": "1", "lithiumMode": "0", "safetyType": "2", "inverterType": "5",
                "sellTime1": "00:00", "sellTime2": "04:00", "sellTime3": "08:00",
                "sellTime4": "12:00", "sellTime5": "16:00", "sellTime6": "20:00",
                "sellTime1Pac": "5000", "sellTime2Pac": "5000", "sellTime3Pac": "5000",
                "sellTime4Pac": "5000", "sellTime5Pac": "5000", "sellTime6Pac": "5000",
                "sellTime1Volt": "49", "sellTime2Volt": "49", "sellTime3Volt": "49",
                "sellTime4Volt": "49", "sellTime5Volt": "49", "sellTime6Volt": "49",
                "cap1": "100", "cap2": "40", "cap3": "40", "cap4": "40", "cap5": "40", "cap6": "40",
                "time1on": True, "time2on": False, "time3on": "false", "time4on": "false",
                "time5on": "false", "time6on": "false",
                "genTime1on": False, "genTime2on": False, "genTime3on": False,
                "genTime4on": False, "genTime5on": False, "genTime6on": False,
                "mondayOn": True, "tuesdayOn": True, "wednesdayOn": True, "thursdayOn": True,
                "fridayOn": True, "saturdayOn": True, "sundayOn": True,
                "beep": "0", "someUnknownSetting": "42",
            },
        })

    async def set_inverter_settings(self, request):
        body = await request.json()
        self.settings_writes.append(body)
        return self._json({"code": 0, "msg": "Success", "success": True, "data": None})

    async def get_plant_realtime(self, request):
        assert request.query.get('id') == '12345'
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {
                "pac": 2484, "efficiency": 0.75, "etoday": 9.0, "emonth": 120.5, "eyear": 1500.25,
                "etotal": 5622.3, "totalPower": 3.68, "currency": {"id": 1, "code": "GBP", "text": "GBP"},
                "invest": 0.0, "income": 12.34, "updateAt": "2023-01-07T16:50:17Z",
            },
        })

    async def get_plant_energy_day(self, request):
        assert request.query.get('date') == '2026-07-07'
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {"infos": [
                {"unit": "W", "label": "PV", "records": [
                    {"time": "2026-07-07 10:00:00", "value": "100"},
                    {"time": "2026-07-07 10:05:00", "value": "200"}]},
                {"unit": "W", "label": "Load", "records": [
                    {"time": "2026-07-07 10:00:00", "value": "300"},
                    {"time": "2026-07-07 10:05:00", "value": "400"}]},
            ]},
        })

    async def get_plant_energy_month(self, request):
        assert request.query.get('date') == '2026-07'
        return self._json({
            "code": 0, "msg": "Success", "success": True,
            "data": {"infos": [
                {"unit": "kWh", "label": "PV", "records": [
                    {"time": "2026-07-01", "value": "10.5"},
                    {"time": "2026-07-02", "value": "12.0"}]},
            ]},
        })

    async def set_plant_income(self, request):
        body = await request.json()
        self.income_writes.append(body)
        return self._json({"code": 0, "msg": "Success", "success": True, "data": None})


class PagedMockApiServer(MockApiServer):
    """Mock server that reports 25 inverters and 12 plants across several pages."""

    INVERTER_TOTAL = 25
    PLANT_TOTAL = 12

    async def get_inverters(self, request):
        page = int(request.query['page'])
        limit = int(request.query['limit'])
        start = (page - 1) * limit
        infos = [{"sn": f"SN{i:03d}", "gsn": f"G{i:03d}", "plant": {"id": 12345, "name": "John Smith"}}
                 for i in range(start, min(start + limit, self.INVERTER_TOTAL))]
        return self._json({"code": 0, "msg": "Success", "success": True,
                           "data": {"pageSize": limit, "pageNumber": page,
                                    "total": self.INVERTER_TOTAL, "infos": infos}})

    async def get_plants(self, request):
        page = int(request.query['page'])
        limit = int(request.query['limit'])
        start = (page - 1) * limit
        infos = [{"id": i, "name": f"Plant {i}"} for i in range(start, min(start + limit, self.PLANT_TOTAL))]
        return self._json({"code": 0, "msg": "Success", "success": True,
                           "data": {"pageSize": limit, "pageNumber": page,
                                    "total": self.PLANT_TOTAL, "infos": infos}})


class ExpiringTokenMockApiServer(MockApiServer):
    """Mock server whose tokens expire immediately, so every request needs a new login."""

    def __init__(self, aiohttp_client):
        super().__init__(aiohttp_client)
        self.login_count = 0

    async def login(self, request):
        self.login_count += 1
        response = await super().login(request)
        payload = json.loads(response.text)
        if payload.get('success'):
            payload['data']['access_token'] = f'AT{self.login_count}'
            payload['data']['expires_in'] = 1
        return self._json(payload)


class FlakyMockApiServer(MockApiServer):
    """Mock server that rejects the first authenticated request with HTTP 401."""

    def __init__(self, aiohttp_client):
        super().__init__(aiohttp_client)
        self.login_count = 0
        self.unauthorized_responses = 1
        self.app.router.add_get('/api/v1/error', self.get_error)
        self.app.router.add_get('/api/v1/server-error', self.get_server_error)
        self.app.router.add_get('/api/v1/not-json', self.get_not_json)

    async def login(self, request):
        self.login_count += 1
        return await super().login(request)

    async def get_inverters(self, request):
        if self.unauthorized_responses > 0:
            self.unauthorized_responses -= 1
            return web.Response(status=401)
        return await super().get_inverters(request)

    async def get_error(self, request):
        payload = {'code': 500, 'msg': 'Something went wrong', 'success': False}
        return web.Response(text=json.dumps(payload), headers={'Content-Type': 'application/json'})

    async def get_server_error(self, request):
        return web.Response(status=500)

    async def get_not_json(self, request):
        return web.Response(text='<html></html>', headers={'Content-Type': 'text/html'})
