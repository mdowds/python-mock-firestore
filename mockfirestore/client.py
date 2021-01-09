from typing import Iterable
from mockfirestore.collection import CollectionReference
from mockfirestore.document import DocumentReference, DocumentSnapshot
from mockfirestore.transaction import Transaction


class MockFirestore:

    def __init__(self) -> None:
        self._data = {}

    def collection(self, name: str) -> CollectionReference:
        if name not in self._data:
            self._data[name] = {}
        return CollectionReference(self._data, [name])

    def reset(self):
        self._data = {}

    def get_all(self, references: Iterable[DocumentReference],
                field_paths=None,
                transaction=None) -> Iterable[DocumentSnapshot]:
        for doc_ref in set(references):
            yield doc_ref.get()

    def transaction(self, **kwargs) -> Transaction:
        return Transaction(self, **kwargs)


