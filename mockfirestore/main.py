import operator
import random
import string
from collections import OrderedDict
from functools import reduce
from itertools import islice
from typing import (Dict, Any, List, Tuple, TypeVar, Sequence, Callable, Optional,
                    Iterator, Iterable)
import warnings

T = TypeVar('T')
KeyValuePair = Tuple[str, Dict[str, Any]]
Document = Dict[str, Any]
Collection = Dict[str, Document]
Store = Dict[str, Collection]


class DocumentSnapshot:
    def __init__(self, reference: 'DocumentReference', data: Document) -> None:
        self.reference = reference
        self._doc = data

    @property
    def exists(self) -> bool:
        return self._doc != {}

    def to_dict(self) -> Document:
        return self._doc


class DocumentReference:
    def __init__(self, data: Store, path: List[str]) -> None:
        self._data = data
        self._path = path

    @property
    def id(self):
        return self._path[-1]

    def get(self) -> DocumentSnapshot:
        return DocumentSnapshot(self, get_by_path(self._data, self._path))

    def delete(self):
        delete_by_path(self._data, self._path)

    def set(self, data: Dict, merge=False):
        if merge:
            self.update(data)
        else:
            set_by_path(self._data, self._path, data)

    def update(self, data: Dict[str, Any]):
        get_by_path(self._data, self._path).update(data)

    def collection(self, name) -> 'CollectionReference':
        document = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in document:
            set_by_path(self._data, new_path, {})
        return CollectionReference(self._data, new_path)


class Query:
    def __init__(self, parent: 'CollectionReference', projection=None,
                 field_filters=(), orders=(), limit=None, offset=None,
                 start_at=None, end_at=None, all_descendants=False) -> None:
        self.parent = parent
        self.projection = projection
        self._field_filters = []
        self.orders = list(orders)
        self._limit = limit
        self.offset = offset
        self.start_at = start_at
        self.end_at = end_at
        self.all_descendants = all_descendants

        if field_filters:
            for field_filter in field_filters:
                self._add_field_filter(*field_filter)

    @property
    def _data(self) -> OrderedDict:
        data = get_by_path(self.parent._data, self.parent._path)
        if not isinstance(data, OrderedDict):
            data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

        for field, compare, value in self._field_filters:
            data = OrderedDict((k, v) for k, v in data.items() if compare(v[field], value))

        if self.orders:
            for key, direction in self.orders:
                sorted_items = sorted(data.items(),
                                      key=lambda doc: doc[1][key],
                                      reverse=direction == 'DESCENDING')
                data = OrderedDict(sorted_items)

        if self._limit:
            limited = islice(data.items(), self._limit)
            data = OrderedDict(limited)

        return data

    def stream(self) -> Iterator[DocumentSnapshot]:
        doc_refs = self.parent.list_documents()
        return (DocumentSnapshot(doc_ref, doc) for doc_ref, doc
                in zip(doc_refs, self._data.values()))

    def get(self) -> Iterator[DocumentSnapshot]:
        warnings.warn('Query.get is deprecated, please use Query.stream',
                      category=DeprecationWarning)
        return self.stream()

    def _add_field_filter(self, field: str, op: str, value: Any):
        compare = self._compare_func(op)
        self._field_filters.append((field, compare, value))

    def where(self, field: str, op: str, value: Any) -> 'Query':
        self._add_field_filter(field, op, value)
        return self

    def order_by(self, key: str, direction: Optional[str] = 'ASCENDING') -> 'Query':
        self.orders.append((key, direction))
        return self

    def limit(self, limit_amount: int) -> 'Query':
        self._limit = limit_amount
        return self

    def _compare_func(self, op: str) -> Callable[[T, T], bool]:
        if op == '==':
            return lambda x, y: x == y
        elif op == '<':
            return lambda x, y: x < y
        elif op == '<=':
            return lambda x, y: x <= y
        elif op == '>':
            return lambda x, y: x > y
        elif op == '>=':
            return lambda x, y: x >= y


class CollectionReference:
    def __init__(self, data: Store, path: List[str]) -> None:
        self._data = data
        self._path = path

    def document(self, name: Optional[str] = None) -> DocumentReference:
        collection = get_by_path(self._data, self._path)
        if name is None:
            name = generate_random_string()
        new_path = self._path + [name]
        if name not in collection:
            set_by_path(self._data, new_path, {})
        return DocumentReference(self._data, new_path)

    def get(self) -> Iterator[DocumentSnapshot]:
        return Query(self).get()

    def where(self, field: str, op: str, value: Any) -> Query:
        query = Query(self, field_filters=[(field, op, value)])
        return query

    def order_by(self, key: str, direction: Optional[str] = None) -> Query:
        query = Query(self, orders=[(key, direction)])
        return query

    def limit(self, limit_amount: int) -> Query:
        query = Query(self, limit=limit_amount)
        return query

    def list_documents(self, page_size: Optional[int] = None) -> Sequence[DocumentReference]:
        docs = []
        for key in get_by_path(self._data, self._path):
            docs.append(self.document(key))
        return docs

    def stream(self, transaction=None) -> Iterable[DocumentSnapshot]:
        for key in get_by_path(self._data, self._path):
            doc_snapshot = self.document(key).get()
            yield doc_snapshot


class MockFirestore:

    def __init__(self) -> None:
        self._data = {}

    def collection(self, name: str) -> CollectionReference:
        if name not in self._data:
            self._data[name] = {}
        return CollectionReference(self._data, [name])

    def reset(self):
        self._data = {}


def get_by_path(data: Dict[str, T], path: Sequence[str]) -> T:
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, path, data)


def set_by_path(data: Dict[str, T], path: Sequence[str], value: T):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(data, path[:-1])[path[-1]] = value


def delete_by_path(data: Dict[str, T], path: Sequence[str]):
    """Delete a value in a nested object in root by item sequence."""
    del get_by_path(data, path[:-1])[path[-1]]


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
