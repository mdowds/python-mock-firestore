from typing import Optional, List, Tuple, Dict, AsyncIterator
from mockfirestore.async_document import AsyncDocumentReference
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
        for doc_snapshot in super().stream():
            yield doc_snapshot
