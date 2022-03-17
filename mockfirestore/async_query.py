from typing import AsyncIterator, List
from mockfirestore.document import DocumentSnapshot
from mockfirestore.query import Query


class AsyncQuery(Query):
    async def stream(self, transaction=None) -> AsyncIterator[DocumentSnapshot]:
        doc_snapshots = self.parent.stream()
        for field, compare, value in self._field_filters:
            doc_snapshots = [doc_snapshot async for doc_snapshot in doc_snapshots
                             if compare(doc_snapshot._get_by_field_path(field), value)]

        doc_snapshots = super()._process_pagination(doc_snapshots)
        for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def get(self, transaction=None) -> List[DocumentSnapshot]:
        return super().get()



