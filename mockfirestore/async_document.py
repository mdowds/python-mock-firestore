from copy import deepcopy
from typing import Dict, Any
from mockfirestore import NotFound
from mockfirestore.document import DocumentReference, DocumentSnapshot


class AsyncDocumentReference(DocumentReference):
    async def get(self) -> DocumentSnapshot:
        return super().get()

    async def delete(self):
        super().delete()

    async def set(self, data: Dict[str, Any], merge=False):
        if merge:
            try:
                await self.update(deepcopy(data))
            except NotFound:
                await self.set(data)
        else:
            super().set(data, merge=merge)

    async def update(self, data: Dict[str, Any]):
        super().update(data)

    def collection(self, name) -> 'AsyncCollectionReference':
        from mockfirestore.async_collection import AsyncCollectionReference
        coll_ref = super().collection(name)
        return AsyncCollectionReference(coll_ref._data, coll_ref._path, self)
