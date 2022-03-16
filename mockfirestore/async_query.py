from typing import AsyncIterator, List
from mockfirestore.document import DocumentSnapshot
from mockfirestore.query import Query


class AsyncQuery(Query):
    async def stream(self, transaction=None) -> AsyncIterator[DocumentSnapshot]:
        doc_snapshots = super().stream()
        for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def get(self, transaction=None) -> List[DocumentSnapshot]:
        return super().get()



