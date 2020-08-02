# by analogy with
# https://github.com/mongomock/mongomock/blob/develop/mongomock/__init__.py
# try to import gcloud exceptions
# and if gcloud is not installed, define our own
try:
    from google.cloud.exceptions import ClientError, Conflict, AlreadyExists
except ImportError:
    from mockfirestore.exceptions import ClientError, Conflict, AlreadyExists

from mockfirestore.client import MockFirestore
from mockfirestore.document import DocumentSnapshot, DocumentReference
from mockfirestore.collection import CollectionReference
from mockfirestore.query import Query
from mockfirestore._helpers import Timestamp
