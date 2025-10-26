class Snapshot:
    def __init__(self, snapshot_id: str, source: str, status: str = "ready"):
        self.snapshot_id = snapshot_id
        self.source = source
        self.status = status if isinstance(status, str) else status.value
    def to_dict(self) -> dict:
        return {
            'snapshot_id': self.snapshot_id,
            'source': self.source,
            'status': self.status
        }
    @staticmethod
    def from_dict(data: dict) -> 'Snapshot':
        return Snapshot(data['snapshot_id'], data['source'], data['status'] if isinstance(data['status'], str) else Status(data['status']).value)