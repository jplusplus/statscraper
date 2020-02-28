"""Tests for scraper base class."""
from unittest import TestCase
from statscraper import (BaseScraper, Dataset, Dimension, Result,
                         DimensionValue, Collection, ROOT, NoSuchItem)


class Scraper(BaseScraper):
    """A scraper with hardcoded yields."""

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")
        yield Dataset("Dataset_3")

    def _fetch_dimensions(self, dataset):
        yield Dimension("date")

        # Assign a label to one of the allowed values
        mun = Dimension("municipality", allowed_values=[
            "Umeå kommun",
            "Robertsfors kommun"])
        mun.allowed_values["Robertsfors kommun"].label = "Robertsfors kommun"
        yield mun

        yield Dimension("gender")

    def _fetch_allowed_values(self, dimension):
        if dimension.id == "gender":
            yield DimensionValue("male", dimension, label="Men")
            yield DimensionValue("female", dimension, label="Women")

    def _fetch_data(self, dataset, query=None):
        if dataset.id == "Dataset_1":
            yield Result(127, {
                "date": "2017-08-10",
                "municipality": "Robertsfors kommun",
            })
        elif dataset.id == "Dataset_2":
            yield Result(12, {
                "date": "2017-02-06",
                "municipality": "Umeå kommun",
            })
            yield Result(130, {
                "date": "2017-02-07",
                "municipality": "Robertsfors kommun",
            })


class NestedScraper(Scraper):
    """A scraper with hardcoded yields.

    ROOT - Collection_1 - Dataset_1
         - Collection_2 - [Dataset_2, Dataset_3]
    """

    def _fetch_itemslist(self, item):
        if item.id == ROOT:
            yield Collection("Collection_1")
            yield Collection("Collection_2")
        elif item.id == "Collection_1":
            yield Dataset("Dataset_1")
        elif item.id == "Collection_2":
            yield Dataset("Dataset_2")
            yield Dataset("Dataset_3")
        else:
            raise Exception("This can not possibly happen.")


class CallbackScraper(Scraper):
    """A scraper with callbacks."""

    @BaseScraper.on("init")
    def initiation_code(self):
        self.initiated = True

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")


class TestBaseScraper(TestCase):
    """Testing base functionality."""

    def test_init(self):
        """Extending the basescraper."""
        scraper = Scraper()
        self.assertTrue(scraper.current_item.id == ROOT)

    def test_inspect_item(self):
        """Fetching items from an itemlist."""
        scraper = Scraper()
        self.assertTrue(scraper.items[0] == scraper.items["Dataset_1"])

    def test_move_to_item(self):
        """Moving the cursor up and down the tree."""
        scraper = Scraper()
        scraper.move_to("Dataset_1")
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_1")

        scraper.move_up()
        scraper.move_to(1)
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_2")

        scraper.move_up()
        scraper.move_to(scraper.items[2])
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_3")

    def test_chained_move_to(self):
        """Use chaining to move."""
        scraper = Scraper()
        scraper.move_to("Dataset_1").move_up().move_to("Dataset_2")
        self.assertTrue(scraper.current_item.id == "Dataset_2")

    def test_stop_at_root(self):
        """Trying to move up from the root should do nothing."""
        scraper = Scraper()
        scraper.move_up().move_up().move_up().move_up()
        self.assertTrue(scraper.current_item.is_root)

    def test_itemslist_contains(self):
        """Make sure 'in' keyword works with ItemList."""
        scraper = Scraper()
        self.assertTrue("Dataset_1" in scraper.items)
        self.assertTrue(scraper.items[0] in scraper.items)

    def test_select_missing_item(self):
        """Select an Item by ID that doesn't exist."""
        scraper = Scraper()
        with self.assertRaises(NoSuchItem):
            scraper.move_to("non_existing_item")

    def test_item_knows_parent(self):
        """Make sure an item knows who its parent is."""
        scraper = Scraper()
        parent = scraper.current_item
        dataset = scraper["Dataset_1"]
        scraper.move_to("Dataset_1")
        self.assertTrue(scraper.parent.id == dataset.parent.id ==
                        scraper.current_item.parent.id == parent.id)

    def test_fetch_dataset(self):
        """Query a dataset for some data."""
        scraper = Scraper()
        dataset = scraper[0]
        self.assertEqual(dataset.data[0]["municipality"], "Robertsfors kommun")

    def test_unselected_visible_dataset(self):
        """Query a dataset not selected, but visible."""
        scraper = Scraper()
        dataset = scraper["Dataset_1"]
        scraper.move_to("Dataset_2")
        self.assertEqual(dataset.data[0]["municipality"], "Robertsfors kommun")

    def test_cached_data(self):
        """Query a dataset not selected but cached."""
        scraper = Scraper()
        data_1 = scraper["Dataset_1"].data
        scraper.move_up().move_to("Dataset_2")
        self.assertEqual(data_1[0]["municipality"], "Robertsfors kommun")

    def test_get_dimension(self):
        """Get dimensions for a dataset."""
        scraper = Scraper()
        dataset = scraper[0]
        self.assertTrue(len(dataset.dimensions))
        self.assertTrue(isinstance(dataset.dimensions[0], Dimension))

        dim = dataset.dimensions["municipality"]
        self.assertTrue(isinstance(dim, Dimension))

        dim = dataset.dimensions.get("municipality")
        self.assertTrue(isinstance(dim, Dimension))

    def test_select_allowed_values(self):
        """List allowed values from dimension."""
        scraper = Scraper()
        dataset = scraper[0]

        municipality = dataset.dimensions["municipality"]
        self.assertTrue("Robertsfors kommun" in municipality.allowed_values)

        allowed_value = municipality.allowed_values["Robertsfors kommun"]
        self.assertEqual(allowed_value, "Robertsfors kommun")

        # We also want to be able to fetch allowed values by label
        allowed_value_by_label = municipality.allowed_values.get_by_label("Robertsfors kommun")
        self.assertEqual(allowed_value, allowed_value_by_label)

        gender = dataset.dimensions["gender"]
        self.assertEqual(len(gender.allowed_values), 2)

        # Get an allowed value by key
        female = gender.allowed_values["female"]

        # Get an allowed value by label
        female_by_label = gender.allowed_values.get_by_label("Women")

        # The two methods above should fetch the same item
        self.assertEqual(female, female_by_label)
        self.assertEqual(female.id, "gender")
        self.assertEqual(female.value, "female")
        self.assertEqual(female.label, "Women")

    def test_move_deep_manually(self):
        """Use the NestedScraper to move more than one step."""
        scraper = NestedScraper()
        scraper.move_to("Collection_1")
        self.assertTrue("Dataset_1" in scraper.items)

        scraper.move_to("Dataset_1")
        self.assertEqual("Dataset_1", scraper.current_item)
        self.assertTrue(len(scraper.current_item.data))

        scraper.move_to_top().move_to("Collection_2")
        self.assertTrue("Dataset_2" in scraper.items)
        self.assertTrue("Dataset_3" in scraper.items)

        scraper.move_up().move_to("Collection_1")
        self.assertTrue("Dataset_1" in scraper.items)

    def test_move_deep_automatically(self):
        """Use the NestedScraper to move more than one step,
        and make sure the cursor follows along as needed."""
        scraper = NestedScraper()

        collection_2 = scraper.items["Collection_2"]
        self.assertTrue(len(collection_2.items))

        scraper.move_to_top()
        dataset_1 = scraper["Collection_1"]["Dataset_1"]
        self.assertTrue(len(dataset_1.data))

        dataset_2 = collection_2["Dataset_2"]
        self.assertTrue(len(dataset_2.data))

        self.assertTrue(len(dataset_1.data))

    def test_callbacks(self):
        """Extending the basescraper."""
        scraper = CallbackScraper()
        self.assertTrue(scraper.initiated)
