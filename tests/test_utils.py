import gzip
import json

import vcr


def scrub_response():
    def before_record_response(response):
        body = json.loads(gzip.decompress(response['body']['string']).decode('utf8'))
        if 'data' in body.keys() and 'access_token' in body['data'].keys():
            body['data']['access_token'] = 'XXX'
        if 'data' in body.keys() and 'refresh_token' in body['data'].keys():
            body['data']['refresh_token'] = 'XXX'

        response['body']['string'] = gzip.compress(json.dumps(body).encode())

        if 'authorization' in response['headers'].keys():
            response['headers']['authorization'] = 'XXX'
        if 'EagleId' in response['headers'].keys():
            response['headers']['EagleId'] = 'XXX'
        return response
    return before_record_response


def scrub_request(request):
    if request.body:
        body = json.loads(request.body)
        if 'username' in body.keys():
            body['username'] = 'user@example.com'
        if 'password' in body.keys():
            body['password'] = 'letmein'
        request.body = json.dumps(body)
    return request


def sunsynk_vcr():
    return vcr.VCR(
        before_record_response=scrub_response(),
        before_record_request=scrub_request
    )