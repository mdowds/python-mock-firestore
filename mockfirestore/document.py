from copy import deepcopy
from functools import reduce
import operator
from typing import List, Dict, Any
from mockfirestore import NotFound
from mockfirestore._helpers import (
    Timestamp, Document, Store, get_by_path, set_by_path, delete_by_path
)
from mockfirestore._transformations import apply_transformations


class DocumentSnapshot:
    def __init__(self, reference: 'DocumentReference', data: Document) -> None:
        self.reference = reference
        self._doc = deepcopy(data)

    @property
    def id(self):
        return self.reference.id

    @property
    def exists(self) -> bool:
        return self._doc != {}

    def to_dict(self) -> Document:
        return self._doc

    @property
    def create_time(self) -> Timestamp:
        timestamp = Timestamp.from_now()
        return timestamp

    @property
    def update_time(self) -> Timestamp:
        return self.create_time

    @property
    def read_time(self) -> Timestamp:
        timestamp = Timestamp.from_now()
        return timestamp

    def get(self, field_path: str) -> Any:
        if not self.exists:
            return None
        else:
            return reduce(operator.getitem, field_path.split('.'), self._doc)

    def _get_by_field_path(self, field_path: str) -> Any:
        try:
            return self.get(field_path)
        except KeyError:
            return None


class DocumentReference:
    def __init__(self, data: Store, path: List[str],
                 parent: 'CollectionReference') -> None:
        self._data = data
        self._path = path
        self.parent = parent

    @property
    def id(self):
        return self._path[-1]

    def get(self) -> DocumentSnapshot:
        return DocumentSnapshot(self, get_by_path(self._data, self._path))

    def delete(self):
        delete_by_path(self._data, self._path)

    def set(self, data: Dict, merge=False):
        if merge:
            try:
                self.update(deepcopy(data))
            except NotFound:
                self.set(data)
        else:
            set_by_path(self._data, self._path, deepcopy(data))

    def update(self, data: Dict[str, Any]):
        document = get_by_path(self._data, self._path)
        if document == {}:
            raise NotFound('No document to update: {}'.format(self._path))

        apply_transformations(document, deepcopy(data))

    def collection(self, name) -> 'CollectionReference':
        from mockfirestore.collection import CollectionReference
        document = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in document:
            set_by_path(self._data, new_path, {})
        return CollectionReference(self._data, new_path, parent=self)
