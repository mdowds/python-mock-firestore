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
