from typing import AsyncIterable, Iterable

from mockfirestore.async_document import AsyncDocumentReference
from mockfirestore.document import DocumentSnapshot
from mockfirestore.transaction import Transaction, WriteResult


class AsyncTransaction(Transaction):
    async def _begin(self, retry_id=None):
        return super()._begin()

    async def _rollback(self):
        super()._rollback()

    async def _commit(self) -> Iterable[WriteResult]:
        return super()._commit()

    async def get(self, ref_or_query) -> AsyncIterable[DocumentSnapshot]:
        doc_snapshots = super().get(ref_or_query)
        for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def get_all(
        self, references: Iterable[AsyncDocumentReference]
    ) -> AsyncIterable[DocumentSnapshot]:
        doc_snapshots = super().get_all(references)
        for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()



