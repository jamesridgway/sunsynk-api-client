import datetime

from sunsynk.resource import Resource


class Plant(Resource):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.thumb_url = data.get('thumbUrl')
        self.status = data.get('status')
        self.address = data.get('address')
        
        realtime = data.get('realtime') or {}
        self.pac = data.get('pac') if 'pac' in data else realtime.get('pac')
        self.efficiency = data.get('efficiency') if 'efficiency' in data else realtime.get('efficiency')
        self.generation_today = data.get('etoday') if 'etoday' in data else realtime.get('etoday')
        self.generation_total = data.get('etotal') if 'etotal' in data else realtime.get('etotal')
        
        update_at_str = data.get('updateAt') or realtime.get('updateAt')
        if update_at_str:
            self.updated_at = datetime.datetime.strptime(update_at_str, "%Y-%m-%dT%H:%M:%SZ")
        else:
            self.updated_at = None
            
        create_at_str = data.get('createAt')
        if create_at_str:
            self.created_at = datetime.datetime.fromisoformat(create_at_str)
        else:
            self.created_at = None
            
        self.type = data.get('type')
        
        if 'masterId' in data:
            self.master_id = data['masterId']
        elif 'master' in data and data['master']:
            self.master_id = data['master'].get('id')
        else:
            self.master_id = None
            
        self.share = data.get('share')
        self.plant_permissions = data.get('plantPermission')
        self.exist_camera = data.get('existCamera')
        
        self.lon = data.get('lon')
        self.lat = data.get('lat')

