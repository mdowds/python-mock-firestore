import aiounittest

from google.cloud import firestore
from mockfirestore import AsyncMockFirestore, NotFound


class TestAsyncDocumentReference(aiounittest.AsyncTestCase):
    async def test_get_document_by_path(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        doc = await fs.document("foo/first").get()
        self.assertEqual({"id": 1}, doc.to_dict())
        self.assertEqual("first", doc.id)

    async def test_set_document_by_path(self):
        fs = AsyncMockFirestore()
        fs._data = {}
        doc_content = {"id": "bar"}
        await fs.document("foo/doc1/bar/doc2").set(doc_content)
        doc = await fs.document("foo/doc1/bar/doc2").get()
        doc = doc.to_dict()
        self.assertEqual(doc_content, doc)

    async def test_document_get_returnsDocument(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"id": 1}, doc.to_dict())
        self.assertEqual("first", doc.id)

    async def test_document_get_documentIdEqualsKey(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        doc_ref = fs.collection("foo").document("first")
        self.assertEqual("first", doc_ref.id)

    async def test_document_get_newDocumentReturnsDefaultId(self):
        fs = AsyncMockFirestore()
        doc_ref = fs.collection("foo").document()
        doc = await doc_ref.get()
        self.assertNotEqual(None, doc_ref.id)
        self.assertFalse(doc.exists)

    async def test_document_get_documentDoesNotExist(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {}}
        doc = await fs.collection("foo").document("bar").get()
        self.assertEqual({}, doc.to_dict())

    async def test_get_nestedDocument(self):
        fs = AsyncMockFirestore()
        fs._data = {
            "top_collection": {
                "top_document": {
                    "id": 1,
                    "nested_collection": {"nested_document": {"id": 1.1}},
                }
            }
        }
        doc = (
            await fs.collection("top_collection")
            .document("top_document")
            .collection("nested_collection")
            .document("nested_document")
            .get()
        )

        self.assertEqual({"id": 1.1}, doc.to_dict())

    async def test_get_nestedDocument_documentDoesNotExist(self):
        fs = AsyncMockFirestore()
        fs._data = {
            "top_collection": {"top_document": {"id": 1, "nested_collection": {}}}
        }
        doc = (
            await fs.collection("top_collection")
            .document("top_document")
            .collection("nested_collection")
            .document("nested_document")
            .get()
        )

        self.assertEqual({}, doc.to_dict())

    async def test_document_set_setsContentOfDocument(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {}}
        doc_content = {"id": "bar"}
        await fs.collection("foo").document("bar").set(doc_content)
        doc = await fs.collection("foo").document("bar").get()
        self.assertEqual(doc_content, doc.to_dict())

    async def test_document_set_mergeNewValue(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        await fs.collection("foo").document("first").set({"updated": True}, merge=True)
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"id": 1, "updated": True}, doc.to_dict())

    async def test_document_set_mergeNewValueForNonExistentDoc(self):
        fs = AsyncMockFirestore()
        await fs.collection("foo").document("first").set({"updated": True}, merge=True)
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"updated": True}, doc.to_dict())

    async def test_document_set_overwriteValue(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        await fs.collection("foo").document("first").set({"new_id": 1}, merge=False)
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"new_id": 1}, doc.to_dict())

    async def test_document_set_isolation(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {}}
        doc_content = {"id": "bar"}
        await fs.collection("foo").document("bar").set(doc_content)
        doc_content["id"] = "new value"
        doc = await fs.collection("foo").document("bar").get()
        self.assertEqual({"id": "bar"}, doc.to_dict())

    async def test_document_update_addNewValue(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        await fs.collection("foo").document("first").update({"updated": True})
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"id": 1, "updated": True}, doc.to_dict())

    async def test_document_update_changeExistingValue(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        await fs.collection("foo").document("first").update({"id": 2})
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"id": 2}, doc.to_dict())

    async def test_document_update_documentDoesNotExist(self):
        fs = AsyncMockFirestore()
        with self.assertRaises(NotFound):
            await fs.collection("foo").document("nonexistent").update({"id": 2})
        docsnap = await fs.collection("foo").document("nonexistent").get()
        self.assertFalse(docsnap.exists)

    async def test_document_update_isolation(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"nested": {"id": 1}}}}
        update_doc = {"nested": {"id": 2}}
        await fs.collection("foo").document("first").update(update_doc)
        update_doc["nested"]["id"] = 3
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual({"nested": {"id": 2}}, doc.to_dict())

    async def test_document_update_transformerIncrementBasic(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"count": 1}}}
        await fs.collection("foo").document("first").update(
            {"count": firestore.Increment(2)}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {"count": 3})

    async def test_document_update_transformerIncrementNested(self):
        fs = AsyncMockFirestore()
        fs._data = {
            "foo": {
                "first": {
                    "nested": {"count": 1},
                    "other": {"likes": 0},
                }
            }
        }
        await fs.collection("foo").document("first").update(
            {
                "nested": {"count": firestore.Increment(-1)},
                "other": {"likes": firestore.Increment(1), "smoked": "salmon"},
            }
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(
            doc.to_dict(),
            {"nested": {"count": 0}, "other": {"likes": 1, "smoked": "salmon"}},
        )

    async def test_document_update_transformerIncrementNonExistent(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"spicy": "tuna"}}}
        await fs.collection("foo").document("first").update(
            {"count": firestore.Increment(1)}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {"count": 1, "spicy": "tuna"})

    async def test_document_delete_documentDoesNotExistAfterDelete(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        await fs.collection("foo").document("first").delete()
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(False, doc.exists)

    async def test_document_parent(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}}}
        coll = fs.collection("foo")
        document = coll.document("first")
        self.assertIs(document.parent, coll)

    async def test_document_update_transformerArrayUnionBasic(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2]}}}
        await fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayUnion([3, 4])}
        )
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict()["arr"], [1, 2, 3, 4])

    async def test_document_update_transformerArrayUnionNested(self):
        fs = AsyncMockFirestore()
        fs._data = {
            "foo": {
                "first": {
                    "nested": {"arr": [1]},
                    "other": {"labels": ["a"]},
                }
            }
        }
        await fs.collection("foo").document("first").update(
            {
                "nested": {"arr": firestore.ArrayUnion([2])},
                "other": {"labels": firestore.ArrayUnion(["b"]), "smoked": "salmon"},
            }
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(
            doc.to_dict(),
            {
                "nested": {"arr": [1, 2]},
                "other": {"labels": ["a", "b"], "smoked": "salmon"},
            },
        )

    async def test_document_update_transformerArrayUnionNonExistent(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"spicy": "tuna"}}}
        await fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayUnion([1])}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {"arr": [1], "spicy": "tuna"})

    async def test_document_update_nestedFieldDotNotation(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"nested": {"value": 1, "unchanged": "foo"}}}}

        await fs.collection("foo").document("first").update({"nested.value": 2})

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {"nested": {"value": 2, "unchanged": "foo"}})

    async def test_document_update_nestedFieldDotNotationNestedFieldCreation(self):
        fs = AsyncMockFirestore()
        fs._data = {
            "foo": {"first": {"other": None}}
        }  # non-existent nested field is created

        await fs.collection("foo").document("first").update({"nested.value": 2})

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {"nested": {"value": 2}, "other": None})

    async def test_document_update_nestedFieldDotNotationMultipleNested(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"other": None}}}

        await fs.collection("foo").document("first").update(
            {"nested.subnested.value": 42}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(
            doc.to_dict(), {"nested": {"subnested": {"value": 42}}, "other": None}
        )

    async def test_document_update_nestedFieldDotNotationMultipleNestedWithTransformer(
        self,
    ):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"other": None}}}

        await fs.collection("foo").document("first").update(
            {"nested.subnested.value": firestore.ArrayUnion([1, 3])}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(
            doc.to_dict(), {"nested": {"subnested": {"value": [1, 3]}}, "other": None}
        )

    async def test_document_update_transformerSentinel(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"spicy": "tuna"}}}
        await fs.collection("foo").document("first").update(
            {"spicy": firestore.DELETE_FIELD}
        )

        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict(), {})

    async def test_document_update_transformerArrayRemoveBasic(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        await fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayRemove([3, 4])}
        )
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict()["arr"], [1, 2])

    async def test_document_update_transformerArrayRemoveNonExistentField(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        await fs.collection("foo").document("first").update(
            {"arr": firestore.ArrayRemove([5])}
        )
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict()["arr"], [1, 2, 3, 4])

    async def test_document_update_transformerArrayRemoveNonExistentArray(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"arr": [1, 2, 3, 4]}}}
        await fs.collection("foo").document("first").update(
            {"non_existent_array": firestore.ArrayRemove([1, 2])}
        )
        doc = await fs.collection("foo").document("first").get()
        self.assertEqual(doc.to_dict()["arr"], [1, 2, 3, 4])
