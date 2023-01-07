import json

import pytest
from aiohttp import web

from sunsynk.client import SunsynkClient


async def login(request):
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


async def get_inverters(request):
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
                        "id": 51013,
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


async def create_test_sunsynk_client(aiohttp_client, app):
    client = await aiohttp_client(app)
    return await SunsynkClient.create('myuser', 'letmein', base_url=f'http://{client.host}:{client.port}')


@pytest.mark.asyncio
async def test_login(aiohttp_client, event_loop):
    app = web.Application()
    app.router.add_post('/oauth/token', login)
    client = await create_test_sunsynk_client(aiohttp_client, app)
    assert isinstance(client, SunsynkClient)


@pytest.mark.asyncio
async def test_get_inverters(aiohttp_client, event_loop):
    app = web.Application()
    app.router.add_post('/oauth/token', login)
    app.router.add_get('/api/v1/inverters', get_inverters)
    client = await create_test_sunsynk_client(aiohttp_client, app)

    inverters = await client.get_inverters()

    assert inverters[0].sn == '1029384756'
    assert inverters[0].gsn == 'E0192837465'
