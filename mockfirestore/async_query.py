from typing import List, AsyncIterator
from mockfirestore.document import DocumentSnapshot
from mockfirestore.query import Query
from mockfirestore._helpers import consume_async_iterable


class AsyncQuery(Query):
    async def stream(self, transaction=None) -> AsyncIterator[DocumentSnapshot]:
        doc_snapshots = await consume_async_iterable(self.parent.stream())
        doc_snapshots = super()._process_field_filters(doc_snapshots)
        doc_snapshots = super()._process_pagination(doc_snapshots)
        for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def get(self, transaction=None) -> List[DocumentSnapshot]:
        return await consume_async_iterable(self.stream())
