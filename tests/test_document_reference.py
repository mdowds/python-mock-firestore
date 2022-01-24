from unittest import TestCase

from google.cloud import firestore

from mockfirestore import MockFirestore, NotFound


class TestDocumentReference(TestCase):

    def test_get_document_by_path(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.document('foo/first').get()
        self.assertEqual({'id': 1}, doc.to_dict())
        self.assertEqual('first', doc.id)

    def test_set_document_by_path(self):
        fs = MockFirestore()
        fs._data = {}
        doc_content = {'id': 'bar'}
        fs.document('foo/doc1/bar/doc2').set(doc_content)
        doc = fs.document('foo/doc1/bar/doc2').get().to_dict()
        self.assertEqual(doc_content, doc)
        
    def test_document_get_returnsDocument(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.collection('foo').document('first').get()
        self.assertEqual({'id': 1}, doc.to_dict())
        self.assertEqual('first', doc.id)

    def test_document_get_documentIdEqualsKey(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc_ref = fs.collection('foo').document('first')
        self.assertEqual('first', doc_ref.id)

    def test_document_get_newDocumentReturnsDefaultId(self):
        fs = MockFirestore()
        doc_ref = fs.collection('foo').document()
        doc = doc_ref.get()
        self.assertNotEqual(None, doc_ref.id)
        self.assertFalse(doc.exists)

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

    def test_document_set_mergeNewValue(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        fs.collection('foo').document('first').set({'updated': True}, merge=True)
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'id': 1, 'updated': True}, doc)

    def test_document_set_mergeNewValueForNonExistentDoc(self):
        fs = MockFirestore()
        fs.collection('foo').document('first').set({'updated': True}, merge=True)
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'updated': True}, doc)

    def test_document_set_overwriteValue(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        fs.collection('foo').document('first').set({'new_id': 1}, merge=False)
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'new_id': 1}, doc)

    def test_document_set_isolation(self):
        fs = MockFirestore()
        fs._data = {'foo': {}}
        doc_content = {'id': 'bar'}
        fs.collection('foo').document('bar').set(doc_content)
        doc_content['id'] = 'new value'
        doc = fs.collection('foo').document('bar').get().to_dict()
        self.assertEqual({'id': 'bar'}, doc)

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

    def test_document_update_documentDoesNotExist(self):
        fs = MockFirestore()
        with self.assertRaises(NotFound):
            fs.collection('foo').document('nonexistent').update({'id': 2})
        docsnap = fs.collection('foo').document('nonexistent').get()
        self.assertFalse(docsnap.exists)

    def test_document_update_isolation(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'nested': {'id': 1}}
        }}
        update_doc = {'nested': {'id': 2}}
        fs.collection('foo').document('first').update(update_doc)
        update_doc['nested']['id'] = 3
        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual({'nested': {'id': 2}}, doc)

    def test_document_update_transformerIncrementBasic(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'count': 1}
        }}
        fs.collection('foo').document('first').update({'count': firestore.Increment(2)})

        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual(doc, {'count': 3})

    def test_document_update_transformerIncrementNested(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {
                'nested': {'count': 1},
                'other': {'likes': 0},
            }
        }}
        fs.collection('foo').document('first').update({
            'nested': {'count': firestore.Increment(-1)},
            'other': {'likes': firestore.Increment(1), 'smoked': 'salmon'},
        })

        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual(doc, {
            'nested': {'count': 0},
            'other': {'likes': 1, 'smoked': 'salmon'}
        })

    def test_document_update_transformerIncrementNonExistent(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'spicy': 'tuna'}
        }}
        fs.collection('foo').document('first').update({'count': firestore.Increment(1)})

        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual(doc, {'count': 1, 'spicy': 'tuna'})

    def test_document_delete_documentDoesNotExistAfterDelete(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        fs.collection('foo').document('first').delete()
        doc = fs.collection('foo').document('first').get()
        self.assertEqual(False, doc.exists)

    def test_document_parent(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        coll = fs.collection('foo')
        document = coll.document('first')
        self.assertIs(document.parent, coll)

    def test_document_update_transformerArrayUnionBasic(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2]}}}
        fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayUnion([3, 4])}
        )
        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc["arr"], [1, 2, 3, 4])

    def test_document_update_transformerArrayUnionNested(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {
                'nested': {'arr': [1]},
                'other': {'labels': ["a"]},
            }
        }}
        fs.collection('foo').document('first').update({
            'nested': {'arr': firestore.ArrayUnion([2])},
            'other': {'labels': firestore.ArrayUnion(["b"]), 'smoked': 'salmon'},
        })

        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual(doc, {
            'nested': {'arr': [1, 2]},
            'other': {'labels': ["a", "b"], 'smoked': 'salmon'}
        })

    def test_document_update_transformerArrayUnionNonExistent(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'spicy': 'tuna'}
        }}
        fs.collection('foo').document('first').update({'arr': firestore.ArrayUnion([1])})

        doc = fs.collection('foo').document('first').get().to_dict()
        self.assertEqual(doc, {'arr': [1], 'spicy': 'tuna'})

    def test_document_update_nestedFieldDotNotation(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"nested": {"value": 1, "unchanged": "foo"}}}}

        fs.collection("foo").document("first").update({"nested.value": 2})

        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc, {"nested": {"value": 2, "unchanged": "foo"}})

    def test_document_update_nestedFieldDotNotationNestedFieldCreation(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"other": None}}}  # non-existent nested field is created

        fs.collection("foo").document("first").update({"nested.value": 2})

        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc, {"nested": {"value": 2}, "other": None})

    def test_document_update_nestedFieldDotNotationMultipleNested(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"other": None}}}

        fs.collection("foo").document("first").update({"nested.subnested.value": 42})

        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc, {"nested": {"subnested": {"value": 42}}, "other": None})

    def test_document_update_nestedFieldDotNotationMultipleNestedWithTransformer(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"other": None}}}

        fs.collection("foo").document("first").update(
            {"nested.subnested.value": firestore.ArrayUnion([1, 3])}
        )

        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc, {"nested": {"subnested": {"value": [1, 3]}}, "other": None})


    def test_document_update_transformerSentinel(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'spicy': 'tuna'}
        }}
        fs.collection('foo').document('first').update({"spicy": firestore.DELETE_FIELD})

        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc, {})

    def test_document_update_transformerArrayRemoveBasic(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayRemove([3, 4])}
        )
        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc["arr"], [1, 2])

    def test_document_update_transformerArrayRemoveNonExistentField(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayRemove([5])}
        )
        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc["arr"], [1, 2, 3, 4])

    def test_document_update_transformerArrayRemoveNonExistentArray(self):
        fs = MockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        fs.collection("foo").document("first").update(
            {"non_existent_array": firestore.ArrayRemove([1, 2])}
        )
        doc = fs.collection("foo").document("first").get().to_dict()
        self.assertEqual(doc["arr"], [1, 2, 3, 4])

