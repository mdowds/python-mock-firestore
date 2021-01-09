# by analogy with
# https://github.com/mongomock/mongomock/blob/develop/mongomock/__init__.py
# try to import gcloud exceptions
# and if gcloud is not installed, define our own
try:
    from google.api_core.exceptions import ClientError, Conflict, NotFound, AlreadyExists
except ImportError:
    from mockfirestore.exceptions import ClientError, Conflict, NotFound, AlreadyExists

from mockfirestore.client import MockFirestore
from mockfirestore.document import DocumentSnapshot, DocumentReference
from mockfirestore.collection import CollectionReference
from mockfirestore.query import Query
from mockfirestore._helpers import Timestamp
from mockfirestore.transaction import Transaction
