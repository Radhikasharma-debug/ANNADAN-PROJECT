from __future__ import annotations

from copy import deepcopy
from datetime import datetime

try:
    from bson import ObjectId
except Exception:
    class ObjectId(str):
        pass


class MockCursor:
    """Minimal cursor-like wrapper for list results."""

    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, key_or_list, direction=1):
        reverse = direction == -1

        if isinstance(key_or_list, (list, tuple)) and key_or_list and isinstance(key_or_list[0], tuple):
            # Support multi-field sort format: [('field', 1), ('created_at', -1)]
            for key, dir_value in reversed(key_or_list):
                self._docs.sort(key=lambda doc: doc.get(key), reverse=dir_value == -1)
        else:
            self._docs.sort(key=lambda doc: doc.get(key_or_list), reverse=reverse)

        return self

    def skip(self, amount):
        self._docs = self._docs[int(amount) :]
        return self

    def limit(self, amount):
        self._docs = self._docs[: int(amount)]
        return self

    def __iter__(self):
        return iter(self._docs)


class MockCollection:
    """Mock MongoDB collection"""

    def __init__(self, data_store, collection_name):
        self.data_store = data_store
        self.name = collection_name
        self.data_store.setdefault(self.name, [])

    def create_index(self, field_name, **kwargs):
        """No-op for mock index creation"""
        return f"{self.name}_{field_name}_idx"

    def insert_one(self, document):
        """Insert one document"""
        doc = deepcopy(document)
        doc['_id'] = doc.get('_id', ObjectId())
        self.data_store[self.name].append(doc)

        class Result:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id

        return Result(doc['_id'])

    def insert_many(self, documents):
        inserted_ids = []
        for document in documents:
            result = self.insert_one(document)
            inserted_ids.append(result.inserted_id)

        class Result:
            def __init__(self, inserted):
                self.inserted_ids = inserted

        return Result(inserted_ids)

    def find_one(self, query, projection=None):
        """Find one matching document"""
        for doc in self.data_store[self.name]:
            if self._matches(doc, query or {}):
                return self._apply_projection(doc, projection)
        return None

    def find(self, query=None, projection=None):
        """Find matching documents"""
        query = query or {}
        docs = [self._apply_projection(doc, projection) for doc in self.data_store[self.name] if self._matches(doc, query)]
        return MockCursor(docs)

    def update_one(self, query, update):
        """Update first matching document"""
        modified = 0

        for doc in self.data_store[self.name]:
            if self._matches(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        doc[key] = (doc.get(key, 0) or 0) + value
                modified = 1
                break

        class Result:
            def __init__(self, modified_count):
                self.modified_count = modified_count

        return Result(modified)

    def count_documents(self, query):
        query = query or {}
        return sum(1 for doc in self.data_store[self.name] if self._matches(doc, query))

    def aggregate(self, pipeline):
        """Very small subset for current app needs ($match + $group/$avg)."""
        docs = self.data_store[self.name]

        for stage in pipeline:
            if '$match' in stage:
                docs = [doc for doc in docs if self._matches(doc, stage['$match'])]
            elif '$group' in stage:
                group = stage['$group']
                output = {}

                for out_key, operation in group.items():
                    if out_key == '_id':
                        output['_id'] = None
                        continue

                    if isinstance(operation, dict) and '$avg' in operation:
                        expr = operation['$avg']
                        values = []

                        if isinstance(expr, dict) and '$subtract' in expr:
                            left, right = expr['$subtract']
                            left_key = str(left).lstrip('$')
                            right_key = str(right).lstrip('$')
                            for doc in docs:
                                left_val = doc.get(left_key)
                                right_val = doc.get(right_key)
                                if isinstance(left_val, datetime) and isinstance(right_val, datetime):
                                    values.append((left_val - right_val).total_seconds())
                                elif isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                                    values.append(left_val - right_val)
                        else:
                            field = str(expr).lstrip('$')
                            for doc in docs:
                                value = doc.get(field)
                                if isinstance(value, (int, float)):
                                    values.append(value)

                        output[out_key] = (sum(values) / len(values)) if values else 0

                docs = [output]

        return docs

    def _apply_projection(self, doc, projection):
        if projection is None:
            return doc

        include_keys = [k for k, v in projection.items() if v]
        exclude_keys = [k for k, v in projection.items() if not v]

        if include_keys:
            projected = {k: v for k, v in doc.items() if k in include_keys or k == '_id'}
        else:
            projected = deepcopy(doc)

        for key in exclude_keys:
            projected.pop(key, None)

        return projected

    def _matches(self, doc, query):
        for key, expected in (query or {}).items():
            actual = doc.get(key)

            if isinstance(expected, dict):
                if '$in' in expected and actual not in expected['$in']:
                    return False
                if '$eq' in expected and actual != expected['$eq']:
                    return False
                if '$gte' in expected and (actual is None or actual < expected['$gte']):
                    return False
            else:
                if actual != expected:
                    return False

        return True


class MockDB:
    """In-memory mock database for development/testing without MongoDB"""

    def __init__(self):
        self.data = {}

    def __getitem__(self, collection_name):
        return MockCollection(self.data, collection_name)

    def __getattr__(self, collection_name):
        return self.__getitem__(collection_name)

    def create_collection(self, collection_name):
        self.data.setdefault(collection_name, [])
        return MockCollection(self.data, collection_name)

    def list_collection_names(self):
        return list(self.data.keys())

    def get_collection(self, collection_name):
        return self.__getitem__(collection_name)


# Export mock database singleton
mock_db = MockDB()
