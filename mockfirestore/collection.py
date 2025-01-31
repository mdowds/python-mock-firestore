import warnings
from typing import Any, List, Optional, Iterable, Dict, Tuple, Sequence, Union

from mockfirestore import AlreadyExists
from mockfirestore._helpers import generate_random_string, Store, get_by_path, set_by_path, Timestamp
from mockfirestore.query import Query
from mockfirestore.document import DocumentReference, DocumentSnapshot


class CollectionReference:
    def __init__(self, data: Store, path: List[str],
                 parent: Optional[DocumentReference] = None) -> None:
        self._data = data
        self._path = path
        self.parent = parent
        self.id = None
        if len(path):
            self.id = path[0]

    def document(self, document_id: Optional[str] = None) -> DocumentReference:
        collection = get_by_path(self._data, self._path)
        if document_id is None:
            document_id = generate_random_string()
        new_path = self._path + [document_id]
        if document_id not in collection:
            set_by_path(self._data, new_path, {})
        return DocumentReference(self._data, new_path, parent=self)

    def get(self) -> Iterable[DocumentSnapshot]:
        warnings.warn('Collection.get is deprecated, please use Collection.stream',
                      category=DeprecationWarning)
        return self.stream()

    def add(self, document_data: Dict, document_id: str = None) \
            -> Tuple[Timestamp, DocumentReference]:
        if document_id is None:
            document_id = document_data.get('id', generate_random_string())
        collection = get_by_path(self._data, self._path)
        new_path = self._path + [document_id]
        if document_id in collection:
            raise AlreadyExists('Document already exists: {}'.format(new_path))
        doc_ref = DocumentReference(self._data, new_path, parent=self)
        doc_ref.set(document_data)
        timestamp = Timestamp.from_now()
        return timestamp, doc_ref

    def where(self, field: str, op: str, value: Any) -> Query:
        query = Query(self, field_filters=[(field, op, value)])
        return query

    def order_by(self, key: str, direction: Optional[str] = None) -> Query:
        query = Query(self, orders=[(key, direction)])
        return query

    def limit(self, limit_amount: int) -> Query:
        query = Query(self, limit=limit_amount)
        return query

    def offset(self, offset: int) -> Query:
        query = Query(self, offset=offset)
        return query

    def start_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> Query:
        query = Query(self, start_at=(document_fields_or_snapshot, True))
        return query

    def start_after(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> Query:
        query = Query(self, start_at=(document_fields_or_snapshot, False))
        return query

    def end_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> Query:
        query = Query(self, end_at=(document_fields_or_snapshot, True))
        return query

    def end_before(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> Query:
        query = Query(self, end_at=(document_fields_or_snapshot, False))
        return query

    def list_documents(self, page_size: Optional[int] = None) -> Sequence[DocumentReference]:
        docs = []
        for key in get_by_path(self._data, self._path):
            docs.append(self.document(key))
        return docs

    def stream(self, transaction=None) -> Iterable[DocumentSnapshot]:
        for key in sorted({str(k):v for k,v in get_by_path(self._data, self._path).items()}):
            doc_snapshot = self.document(key).get()
            yield doc_snapshot
