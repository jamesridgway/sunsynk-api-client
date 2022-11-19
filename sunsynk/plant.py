import datetime


class Plant:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.thumbUrl = data['thumbUrl']
        self.status = data['status']
        self.address = data['address']
        self.pac = data['pac']
        self.efficiency = data['efficiency']
        self.generation_today = data['etoday']
        self.generation_total = data['etotal']
        self.updated_at = datetime.datetime.strptime(data['updateAt'], "%Y-%m-%dT%H:%M:%SZ")
        self.created_at = datetime.datetime.fromisoformat(data['createAt'])
        self.type = data['type']
        self.master_id = data['masterId']
        self.share = data['share']
        self.plant_permissions = data['plantPermission']
        self.exist_camera = data['existCamera']

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
            )