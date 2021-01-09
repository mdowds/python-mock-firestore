from unittest import TestCase
from mockfirestore import MockFirestore, Transaction


class TestTransaction(TestCase):
    def setUp(self) -> None:
        self.fs = MockFirestore()
        self.fs._data = {'foo': {
                'first': {'id': 1},
                'second': {'id': 2}
            }}

    def test_transaction_getAll(self):
        with Transaction(self.fs) as transaction:
            transaction._begin()
            docs = [self.fs.collection('foo').document(doc_name)
                    for doc_name in self.fs._data['foo']]
            results = list(transaction.get_all(docs))
            returned_docs_snapshots = [result.to_dict() for result in results]
            expected_doc_snapshots = [doc.get().to_dict() for doc in docs]
            for expected_snapshot in expected_doc_snapshots:
                self.assertIn(expected_snapshot, returned_docs_snapshots)

    def test_transaction_getDocument(self):
        with Transaction(self.fs) as transaction:
            transaction._begin()
            doc = self.fs.collection('foo').document('first')
            returned_doc = next(transaction.get(doc))
            self.assertEqual(doc.get().to_dict(), returned_doc.to_dict())

    def test_transaction_getQuery(self):
        with Transaction(self.fs) as transaction:
            transaction._begin()
            query = self.fs.collection('foo').order_by('id')
            returned_docs = [doc.to_dict() for doc in transaction.get(query)]
            query = self.fs.collection('foo').order_by('id')
            expected_docs = [doc.to_dict() for doc in query.stream()]
            self.assertEqual(returned_docs, expected_docs)

    def test_transaction_set_setsContentOfDocument(self):
        doc_content = {'id': '3'}
        doc_ref = self.fs.collection('foo').document('third')
        with Transaction(self.fs) as transaction:
            transaction._begin()
            transaction.set(doc_ref, doc_content)
        self.assertEqual(doc_ref.get().to_dict(), doc_content)

    def test_transaction_set_mergeNewValue(self):
        doc = self.fs.collection('foo').document('first')
        with Transaction(self.fs) as transaction:
            transaction._begin()
            transaction.set(doc, {'updated': True}, merge=True)
        updated_doc = {'id': 1, 'updated': True}
        self.assertEqual(doc.get().to_dict(), updated_doc)

    def test_transaction_update_changeExistingValue(self):
        doc = self.fs.collection('foo').document('first')
        with Transaction(self.fs) as transaction:
            transaction._begin()
            transaction.update(doc, {'updated': False})
        updated_doc = {'id': 1, 'updated': False}
        self.assertEqual(doc.get().to_dict(), updated_doc)

    def test_transaction_delete_documentDoesNotExistAfterDelete(self):
        doc = self.fs.collection('foo').document('first')
        with Transaction(self.fs) as transaction:
            transaction._begin()
            transaction.delete(doc)
        doc = self.fs.collection('foo').document('first').get()
        self.assertEqual(False, doc.exists)



