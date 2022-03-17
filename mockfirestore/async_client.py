from typing import AsyncIterable, Iterable

from mockfirestore.async_document import AsyncDocumentReference
from mockfirestore.async_collection import AsyncCollectionReference
from mockfirestore.async_transaction import AsyncTransaction
from mockfirestore.client import MockFirestore
from mockfirestore.document import DocumentSnapshot


class AsyncMockFirestore(MockFirestore):
    def document(self, path: str) -> AsyncDocumentReference:
        doc = super().document(path)
        assert isinstance(doc, AsyncDocumentReference)
        return doc

    def collection(self, path: str) -> AsyncCollectionReference:
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
            return AsyncCollectionReference(self._data, [name])

    async def collections(self) -> AsyncIterable[AsyncCollectionReference]:
        for collection_name in self._data:
            yield AsyncCollectionReference(self._data, [collection_name])

    async def get_all(
        self,
        references: Iterable[AsyncDocumentReference],
        field_paths=None,
        transaction=None,
    ) -> AsyncIterable[DocumentSnapshot]:
        for doc_ref in set(references):
            yield await doc_ref.get()

    def transaction(self, **kwargs) -> AsyncTransaction:
        return AsyncTransaction(self, **kwargs)
