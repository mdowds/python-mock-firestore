from typing import Optional, List, Tuple, Dict, AsyncIterator, Any, Union
from mockfirestore.async_document import AsyncDocumentReference
from mockfirestore.async_query import AsyncQuery
from mockfirestore.collection import CollectionReference
from mockfirestore.document import DocumentSnapshot, DocumentReference
from mockfirestore._helpers import Timestamp, get_by_path


class AsyncCollectionReference(CollectionReference):
    def document(self, document_id: Optional[str] = None) -> AsyncDocumentReference:
        doc_ref = super().document(document_id)
        return AsyncDocumentReference(
            doc_ref._data, doc_ref._path, parent=doc_ref.parent
        )

    async def get(self) -> List[DocumentSnapshot]:
        return super().get()

    async def add(
        self, document_data: Dict, document_id: str = None
    ) -> Tuple[Timestamp, AsyncDocumentReference]:
        timestamp, doc_ref = super().add(document_data, document_id=document_id)
        async_doc_ref = AsyncDocumentReference(
            doc_ref._data, doc_ref._path, parent=doc_ref.parent
        )
        return timestamp, async_doc_ref

    async def list_documents(
        self, page_size: Optional[int] = None
    ) -> AsyncIterator[DocumentReference]:
        docs = super().list_documents()
        for doc in docs:
            yield doc

    async def stream(self, transaction=None) -> AsyncIterator[DocumentSnapshot]:
        for key in sorted(get_by_path(self._data, self._path)):
            doc_snapshot = await self.document(key).get()
            yield doc_snapshot

    def where(self, field: str, op: str, value: Any) -> AsyncQuery:
        query = AsyncQuery(self, field_filters=[(field, op, value)])
        return query

    def order_by(self, key: str, direction: Optional[str] = None) -> AsyncQuery:
        query = AsyncQuery(self, orders=[(key, direction)])
        return query

    def limit(self, limit_amount: int) -> AsyncQuery:
        query = AsyncQuery(self, limit=limit_amount)
        return query

    def offset(self, offset: int) -> AsyncQuery:
        query = AsyncQuery(self, offset=offset)
        return query

    def start_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> AsyncQuery:
        query = AsyncQuery(self, start_at=(document_fields_or_snapshot, True))
        return query

    def start_after(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> AsyncQuery:
        query = AsyncQuery(self, start_at=(document_fields_or_snapshot, False))
        return query

    def end_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> AsyncQuery:
        query = AsyncQuery(self, end_at=(document_fields_or_snapshot, True))
        return query

    def end_before(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> AsyncQuery:
        query = AsyncQuery(self, end_at=(document_fields_or_snapshot, False))
        return query
