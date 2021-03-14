from copy import deepcopy
from functools import reduce
import operator
from typing import List, Dict, Any
from mockfirestore import NotFound
from mockfirestore._helpers import (
    Timestamp, Document, Store, get_by_path, set_by_path, delete_by_path, get_document_iterator
)


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

        _apply_transformations(document, deepcopy(data))

    def collection(self, name) -> 'CollectionReference':
        from mockfirestore.collection import CollectionReference
        document = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in document:
            set_by_path(self._data, new_path, {})
        return CollectionReference(self._data, new_path, parent=self)


def _apply_transformations(document: Dict[str, Any], data: Dict[str, Any]):
    """Handles special fields like INCREMENT."""
    increments = {}
    arr_unions = {}

    for key, value in get_document_iterator(data):
        if not value.__class__.__module__.startswith('google.cloud.firestore'):
            # Unfortunately, we can't use `isinstance` here because that would require
            # us to declare google-cloud-firestore as a dependency for this library.
            # However, it's somewhat strange that the mocked version of the library
            # requires the library itself, so we'll just leverage this heuristic as a
            # means of identifying it.
            #
            # Furthermore, we don't hardcode the full module name, since the original
            # library seems to use a thin shim to perform versioning. e.g. at the time
            # of writing, the full module name is `google.cloud.firestore_v1.transforms`,
            # and it can evolve to `firestore_v2` in the future.
            continue

        transformer = value.__class__.__name__
        if transformer == 'Increment':
            increments[key] = value.value
        elif transformer == 'ArrayUnion':
            arr_unions[key] = value.values

        # All other transformations can be applied as needed.
        # See #29 for tracking.
    
    def _update_data(new_values: dict, default: Any):
        for key, value in new_values.items():
            path = key.split('.')

            try:
                item = get_by_path(document, path)
            except (TypeError, KeyError):
                item = default

            set_by_path(data, path, item + value)
    
    _update_data(increments, 0)
    _update_data(arr_unions, [])

    document.update(data)
