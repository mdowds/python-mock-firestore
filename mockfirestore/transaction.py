from functools import partial
import random
from typing import Iterable, Callable
from mockfirestore._helpers import generate_random_string, Timestamp
from mockfirestore.document import DocumentReference, DocumentSnapshot
from mockfirestore.query import Query

MAX_ATTEMPTS = 5
_MISSING_ID_TEMPLATE = "The transaction has no transaction ID, so it cannot be {}."
_CANT_BEGIN = "The transaction has already begun. Current transaction ID: {!r}."
_CANT_ROLLBACK = _MISSING_ID_TEMPLATE.format("rolled back")
_CANT_COMMIT = _MISSING_ID_TEMPLATE.format("committed")


class WriteResult:
    def __init__(self):
        self.update_time = Timestamp.from_now()


class Transaction:
    """
    This mostly follows the model from
    https://googleapis.dev/python/firestore/latest/transaction.html
    """
    def __init__(self, client,
                 max_attempts=MAX_ATTEMPTS, read_only=False):
        self._client = client
        self._max_attempts = max_attempts
        self._read_only = read_only
        self._id = None
        self._write_ops = []
        self.write_results = None

    @property
    def in_progress(self):
        return self._id is not None

    @property
    def id(self):
        return self._id

    def _begin(self, retry_id=None):
        # generate a random ID to set the transaction as in_progress
        self._id = generate_random_string()

    def _clean_up(self):
        self._write_ops.clear()
        self._id = None

    def _rollback(self):
        if not self.in_progress:
            raise ValueError(_CANT_ROLLBACK)

        self._clean_up()

    def _commit(self) -> Iterable[WriteResult]:
        if not self.in_progress:
            raise ValueError(_CANT_COMMIT)

        results = []
        for write_op in self._write_ops:
            write_op()
            results.append(WriteResult())
        self.write_results = results
        self._clean_up()
        return results

    def get_all(self,
                references: Iterable[DocumentReference]) -> Iterable[DocumentSnapshot]:
        return self._client.get_all(references)

    def get(self, ref_or_query) -> Iterable[DocumentSnapshot]:
        if isinstance(ref_or_query, DocumentReference):
            return self._client.get_all([ref_or_query])
        elif isinstance(ref_or_query, Query):
            return ref_or_query.stream()
        else:
            raise ValueError(
                'Value for argument "ref_or_query" must be a DocumentReference or a Query.'
            )

    # methods from
    # https://googleapis.dev/python/firestore/latest/batch.html#google.cloud.firestore_v1.batch.WriteBatch

    def _add_write_op(self, write_op: Callable):
        if self._read_only:
            raise ValueError(
                "Cannot perform write operation in read-only transaction."
            )
        self._write_ops.append(write_op)

    def create(self, reference: DocumentReference, document_data):
        # this is a no-op, because if we have a DocumentReference
        # it's already in the MockFirestore
        ...

    def set(self, reference: DocumentReference, document_data: dict,
            merge=False):
        write_op = partial(reference.set, document_data, merge=merge)
        self._add_write_op(write_op)

    def update(self, reference: DocumentReference,
               field_updates: dict, option=None):
        write_op = partial(reference.update, field_updates)
        self._add_write_op(write_op)

    def delete(self, reference: DocumentReference, option=None):
        write_op = reference.delete
        self._add_write_op(write_op)

    def commit(self):
        return self._commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
