from typing import Iterable, Sequence, Optional
from mockfirestore.collection import CollectionReference
from mockfirestore.document import DocumentReference, DocumentSnapshot
from mockfirestore.transaction import Transaction


class MockFirestore:

    def __init__(self) -> None:
        self._data = {}

    def _ensure_path(self, path):
        current_position = self

        for el in path[:-1]:
            if type(current_position) in (MockFirestore, DocumentReference):
                current_position = current_position.collection(el)
            else:
                current_position = current_position.document(el)

        return current_position

    def document(self, path: str) -> DocumentReference:
        path = path.split("/")

        if len(path) % 2 != 0:
            raise Exception("Cannot create document at path {}".format(path))
        current_position = self._ensure_path(path)

        return current_position.document(path[-1])

    def collection(self, path: str) -> CollectionReference:
        path = path.split("/")

        if len(path) % 2 != 1:
            raise Exception("Cannot create collection at path {}".format(path))

        name = path[-1]
        if len(path) > 1:
            current_position = self._ensure_path(path)
            return current_position.collection(name)
        else:
            if name not in self._data:
                self._data[name] = {}
            return CollectionReference(self._data, [name])

    def collection_group(self, name: str) -> CollectionReference:
        if '/' in name:
            raise Exception("Collection group names cannot contain '/'")

        collection_group_data = _get_collection_group_data(self._data, name)
        data = {name: collection_group_data}

        return CollectionReference(data, [name])

    def collections(self) -> Sequence[CollectionReference]:
        return [CollectionReference(self._data, [collection_name]) for collection_name in self._data]

    def reset(self):
        self._data = {}

    def get_all(self, references: Iterable[DocumentReference],
                field_paths=None,
                transaction=None) -> Iterable[DocumentSnapshot]:
        for doc_ref in set(references):
            yield doc_ref.get()

    def transaction(self, **kwargs) -> Transaction:
        return Transaction(self, **kwargs)


def _get_collection_group_data(data: dict, name: str, output: Optional[dict] = None) -> dict:
    """
    Recursively get the data for a collection group.

    Args:
        data: The root data or document data to search.
        name: The name of the collection group.
        output: The flat output dictionary.

    Returns:
        A flat dictionary containing all the data for the collection group.
    """
    output = output or {}
    if name in data:
        output.update(data[name])
        return output
    else:
        for documents_in_collection in data.values():
            if isinstance(documents_in_collection, dict):
                output.update(_get_collection_group_data(documents_in_collection, name, output))

    return output
