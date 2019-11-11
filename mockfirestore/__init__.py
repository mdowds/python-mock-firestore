try:
    from google.cloud.exceptions import ClientError, Conflict, AlreadyExists
except ImportError:
    from mockfirestore.exceptions import ClientError, Conflict, AlreadyExists

from mockfirestore.client import MockFirestore
from mockfirestore.document import DocumentSnapshot, DocumentReference
from mockfirestore.collection import CollectionReference
from mockfirestore.query import Query
from mockfirestore._helpers import Timestamp
from mockfirestore.transaction import Transaction
