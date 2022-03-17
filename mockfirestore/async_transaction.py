from typing import AsyncIterable, Iterable

from mockfirestore.async_document import AsyncDocumentReference
from mockfirestore.document import DocumentSnapshot
from mockfirestore.transaction import Transaction, WriteResult, _CANT_COMMIT


class AsyncTransaction(Transaction):
    async def _begin(self, retry_id=None):
        return super()._begin()

    async def _rollback(self):
        super()._rollback()

    async def _commit(self) -> Iterable[WriteResult]:
        if not self.in_progress:
            raise ValueError(_CANT_COMMIT)

        results = []
        for write_op in self._write_ops:
            await write_op()
            results.append(WriteResult())
        self.write_results = results
        self._clean_up()
        return results

    async def get(self, ref_or_query) -> AsyncIterable[DocumentSnapshot]:
        doc_snapshots = super().get(ref_or_query)
        async for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def get_all(
        self, references: Iterable[AsyncDocumentReference]
    ) -> AsyncIterable[DocumentSnapshot]:
        doc_snapshots = super().get_all(references)
        async for doc_snapshot in doc_snapshots:
            yield doc_snapshot

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
