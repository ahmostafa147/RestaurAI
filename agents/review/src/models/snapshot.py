class Snapshot:
    def __init__(self, snapshot_id: str, source: str, status: str = "ready", restaurant_id: str = None):
        self.snapshot_id = snapshot_id
        self.source = source
        self.status = status if isinstance(status, str) else status.value
        self.restaurant_id = restaurant_id
    def to_dict(self) -> dict:
        result = {
            'snapshot_id': self.snapshot_id,
            'source': self.source,
            'status': self.status   
        }
        if self.restaurant_id is not None:
            result['restaurant_id'] = self.restaurant_id
        return result
    @staticmethod
    def from_dict(data: dict) -> 'Snapshot':
        return Snapshot(data['snapshot_id'], data['source'], data['status'] if isinstance(data['status'], str) else Status(data['status']).value, data.get('restaurant_id'))