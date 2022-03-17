from typing import Dict, Any
from mockfirestore.document import DocumentReference, DocumentSnapshot


class AsyncDocumentReference(DocumentReference):
    async def get(self) -> DocumentSnapshot:
        return super().get()

    async def delete(self):
        super().delete()

    async def set(self, data: Dict[str, Any], merge=False):
        super().set(data, merge=merge)

    async def update(self, data: Dict[str, Any]):
        super().update(data)

    def collection(self, name) -> 'AsyncCollectionReference':
        from mockfirestore.async_collection import AsyncCollectionReference
        coll_ref = super().collection(name)
        return AsyncCollectionReference(coll_ref._data, coll_ref._path, self)
