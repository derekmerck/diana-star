import json
from datetime import datetime

# Encodes datetime and hashes
class SmartEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        if hasattr(obj, 'hexdigest'):
            return obj.hexdigest()

        return json.JSONEncoder.default(self, obj)