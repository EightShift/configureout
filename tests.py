import unittest
import os
import tempfile
import json
from types import SimpleNamespace
from unittest.mock import patch, mock_open
from configureout import *


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()
        
        # Sample config data
        self.sample_dict = {
            "name": "test",
            "value": 42,
            "nested": {
                "key": "value",
                "numbers": [1, 2, 3]
            }
        }
        
        # Sample JSON string
        self.sample_json = json.dumps(self.sample_dict)
        
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_init_with_dict(self):
        """Test initialization with a dictionary"""
        config = Config(self.sample_dict)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.value, 42)
        self.assertIsInstance(config.nested, Config)
        self.assertEqual(config.nested.key, "value")
        self.assertEqual(config.nested.numbers, [1, 2, 3])

    def test_init_with_json_string(self):
        """Test initialization with a JSON string"""
        config = Config(self.sample_json)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.value, 42)
        self.assertIsInstance(config.nested, Config)

    def test_init_with_file_path(self):
        """Test initialization with a file path"""
        with open(self.temp_path, 'w') as f:
            f.write(self.sample_json)
            
        config = Config(self.temp_path)
        self.assertEqual(config.name, "test")
        self.assertEqual(config._meta_['source_path'], self.temp_path)

    def test_init_with_invalid_source(self):
        """Test initialization with invalid source type"""
        with self.assertRaises(RootConfigTypeError):
            Config(123)

    def test_attribute_access(self):
        """Test attribute access"""
        config = Config(self.sample_dict)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.nested.key, "value")

    def test_item_access(self):
        """Test item access"""
        config = Config(self.sample_dict)
        self.assertEqual(config["name"], "test")
        self.assertEqual(config["nested"]["key"], "value")

    def test_contains(self):
        """Test __contains__ method"""
        config = Config(self.sample_dict)
        self.assertTrue("name" in config)
        self.assertTrue("nested" in config)
        self.assertFalse("missing" in config)

    def test_len(self):
        """Test __len__ method"""
        config = Config(self.sample_dict)
        self.assertEqual(len(config), 3)  # name, value, nested

    def test_iter(self):
        """Test __iter__ method"""
        config = Config(self.sample_dict)
        keys = set(config)
        self.assertEqual(keys, {"name", "value", "nested"})

    def test_str(self):
        """Test __str__ method"""
        config = Config(self.sample_dict)
        str_repr = str(config)
        self.assertIn('"name": "test"', str_repr)
        self.assertIn('"value": 42', str_repr)

    def test_repr(self):
        """Test __repr__ method"""
        config = Config({"single": "value"})
        self.assertIn('Config({"single": ... })', repr(config))
        
        config = Config({"first": 1, "second": 2})
        self.assertIn('Config({"first": ..., ... })', repr(config))
        
        empty_config = Config({})
        self.assertIn('Config(<empty>)', repr(empty_config))

    def test_bool(self):
        """Test __bool__ method"""
        self.assertTrue(bool(Config({"key": "value"})))
        self.assertFalse(bool(Config({})))

    def test_to_dict(self):
        """Test to_dict method"""
        config = Config(self.sample_dict)
        result = config.to_dict()
        self.assertEqual(result, self.sample_dict)
        self.assertIsInstance(result["nested"], dict)

    def test_keys_values_items(self):
        """Test keys(), values(), and items() methods"""
        config = Config(self.sample_dict)
        keys = set(config.keys())
        self.assertEqual(keys, {"name", "value", "nested"})
        
        values = list(config.values())
        self.assertEqual(values[0], "test")
        self.assertEqual(values[1], 42)
        self.assertIsInstance(values[2], Config)
        
        items = dict(config.items())
        self.assertEqual(items["name"], "test")
        self.assertEqual(items["value"], 42)

    def test_get(self):
        """Test get method"""
        config = Config(self.sample_dict)
        self.assertEqual(config.get("name"), "test")
        self.assertEqual(config.get("missing"), None)
        self.assertEqual(config.get("missing", "default"), "default")

    def test_pop(self):
        """Test pop method"""
        config = Config(self.sample_dict)
        value = config.pop("name")
        self.assertEqual(value, "test")
        self.assertNotIn("name", config)
        
        with self.assertRaises(KeyError):
            config.pop("missing")
            
        self.assertEqual(config.pop("missing", "default"), "default")

    def test_popitem(self):
        """Test popitem method"""
        config = Config({"key": "value"})
        item = config.popitem()
        self.assertEqual(item, ("key", "value"))
        self.assertEqual(len(config), 0)

    def test_clear(self):
        """Test clear method"""
        config = Config(self.sample_dict)
        config.clear()
        self.assertEqual(len(config), 0)

    def test_copy(self):
        """Test copy method"""
        config = Config(self.sample_dict)
        copy_config = config.copy()
        self.assertEqual(config.to_dict(), copy_config.to_dict())
        self.assertIsNot(config, copy_config)
        self.assertIsNot(config.nested, copy_config.nested)

    def test_update(self):
        """Test update method"""
        config = Config({"a": 1, "b": 2})
        config.update({"b": 3, "c": 4})
        self.assertEqual(config.a, 1)
        self.assertEqual(config.b, 3)
        self.assertEqual(config.c, 4)
        
        config.update(d=5, e=6)
        self.assertEqual(config.d, 5)
        self.assertEqual(config.e, 6)

    def test_or_operator(self):
        """Test | operator"""
        config1 = Config({"a": 1, "b": 2})
        config2 = Config({"b": 3, "c": 4})
        merged = config1 | config2
        self.assertEqual(merged.a, 1)
        self.assertEqual(merged.b, 3)
        self.assertEqual(merged.c, 4)
        self.assertEqual(config1.b, 2)  # Original unchanged

    def test_ior_operator(self):
        """Test |= operator"""
        config1 = Config({"a": 1, "b": 2})
        config2 = Config({"b": 3, "c": 4})
        config1 |= config2
        self.assertEqual(config1.a, 1)
        self.assertEqual(config1.b, 3)
        self.assertEqual(config1.c, 4)

    def test_save(self):
        """Test save method"""
        # Test saving to original path
        with open(self.temp_path, 'w') as f:
            f.write(self.sample_json)
            
        config = Config(self.temp_path)
        config.name = "modified"
        config.save()
        
        with open(self.temp_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["name"], "modified")
        
        # Test saving to new path
        new_path = self.temp_path + ".new"
        config.save(new_path)
        self.assertTrue(os.path.exists(new_path))
        os.unlink(new_path)
        
        # Test save without path
        config_no_path = Config(self.sample_dict)
        with self.assertRaises(SourcePathError):
            config_no_path.save()

    def test_locked_methods(self):
        """Test protection of locked methods"""
        config = Config(self.sample_dict)
        
        # Test overriding locked methods
        with self.assertRaises(LockedMethodError):
            config.update = "new value"
            
        with self.assertRaises(LockedMethodError):
            config["to_dict"] = "new value"
            
        with self.assertRaises(LockedMethodError):
            config.to_dict = "new value"

    def test_jsonc_parsing(self):
        """Test JSON with comments parsing"""
        jsonc = """
        {
            // This is a comment
            "name": "test", /* multi-line
            comment */
            "value": 42
        }
        """
        config = Config(jsonc)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.value, 42)

    def test_nested_lists(self):
        """Test handling of nested lists"""
        data = {
            "list": [
                {"a": 1},
                {"b": 2}
            ]
        }
        config = Config(data)
        self.assertIsInstance(config.list, list)
        self.assertIsInstance(config.list[0], Config)
        self.assertEqual(config.list[0].a, 1)
        self.assertEqual(config.list[1].b, 2)

if __name__ == '__main__':
    unittest.main()