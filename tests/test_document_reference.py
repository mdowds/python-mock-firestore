from unittest import TestCase

from mockfirestore import MockFirestore


class TestDocumentReference(TestCase):
    def test_document_get_returnsDocument(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'id': 1}, doc)

    def test_document_get_documentDoesNotExist(self):
        fs = MockFirestore()
        fs._data = {'foo': {}}
        doc = fs.collection('foo').document('bar').get().to_dict()
        self.assertEqual({}, doc)

    def test_get_nestedDocument(self):
        fs = MockFirestore()
        fs._data = {'top_collection': {
            'top_document': {
                'id': 1,
                'nested_collection': {
                    'nested_document': {'id': 1.1}
                }
            }
        }}
        doc = fs.collection('top_collection')\
            .document('top_document')\
            .collection('nested_collection')\
            .document('nested_document')\
            .get().to_dict()

        self.assertEqual({'id': 1.1}, doc)

    def test_get_nestedDocument_documentDoesNotExist(self):
        fs = MockFirestore()
        fs._data = {'top_collection': {
            'top_document': {
                'id': 1,
                'nested_collection': {}
            }
        }}
        doc = fs.collection('top_collection')\
            .document('top_document')\
            .collection('nested_collection')\
            .document('nested_document')\
            .get().to_dict()

        self.assertEqual({}, doc)

    def test_document_set_setsContentOfDocument(self):
        fs = MockFirestore()
        fs._data = {'foo': {}}
        doc_content = {'id': 'bar'}
        fs.collection('foo').document('bar').set(doc_content)
        doc = fs.collection('foo').document('bar').get().to_dict()
        self.assertEqual(doc_content, doc)

    def test_document_update_addNewValue(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        fs.collection('foo').document('first').update({'updated': True})
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'id': 1, 'updated': True}, doc)

    def test_document_update_changeExistingValue(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        fs.collection('foo').document('first').update({'id': 2})
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'id': 2}, doc)
