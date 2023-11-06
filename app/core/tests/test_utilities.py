import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
import core.utilities as utils
from core.utilities import env
from core.utilities.logging import LoggingConfigurationBuilder
from core.utilities.test import MockResponse


class TestUtilities(TestCase):
    """Test the base utilities provided."""

    def test_empty(self) -> None:
        """Test the `empty` function."""
        # Test for True
        values = [None, "", "   \n\t   "]
        for value in values:
            with self.subTest("Test for True.", value=value):
                self.assertTrue(utils.empty(value))
        # Test for False
        value = "_value"
        with self.subTest("Test for False.", value=value):
            self.assertFalse(utils.empty(value))

    def test_clear_Nones(self) -> None:
        """Test the `clear_Nones` function."""
        # Test for single values
        for value in ["_value", 1, True]:
            with self.subTest("Test single value.", value=value):
                self.assertEqual(value, utils.clear_Nones(value))
        # Test for objects
        object_value = {"_key1": "_value1", "_key2": None}
        with self.subTest("Test using an object.", object=object_value):
            self.assertEqual({"_key1": "_value1"}, utils.clear_Nones(object_value))
        nested_object = {"_key1": "_value1", "_key2": None, "_nested": {"_nested1": None, "_nested2": "_value2"}}
        with self.subTest("Test using a nested object.", object=nested_object):
            self.assertEqual(
                {"_key1": "_value1", "_nested": {"_nested2": "_value2"}}, utils.clear_Nones(nested_object)
            )
        # Test for lists
        list_value = ["_item1", None, "_item3", None]
        with self.subTest("Test using a list", list=list_value):
            self.assertEqual(["_item1", "_item3"], utils.clear_Nones(list_value))
        nested_list = ["_item1", None, ["_nested1", None]]
        with self.subTest("Test nested lists", value=nested_list):
            self.assertEqual(["_item1", ["_nested1"]], utils.clear_Nones(nested_list))
        # Test combined
        combined_value = ["_item1", "_item2", None, {"_key1": "_value1", "_key2": None}]
        with self.subTest("Test combining lists, objects and nesting.", value=combined_value):
            self.assertEqual(["_item1", "_item2", {"_key1": "_value1"}], utils.clear_Nones(combined_value))
        # Test with kwargs
        with self.subTest("Test with kwargs"):
            self.assertEqual({"_key1": "_value1"}, utils.clear_Nones(_key1="_value1", _key2=None))

    def test_ext(self) -> None:
        """Test the `ext` function."""
        cases = [
            ("_path/_to/_file/_filename._ext", "_ext"),
            ("_path/_file._with._multiple._exts", "_with._multiple._exts"),
            ("_path/_dot._in._the/middle._with_ext", "_with_ext"),
        ]
        for case, expected in cases:
            with self.subTest("Testing the extensions", case=case, ext=expected):
                self.assertEqual(expected, utils.ext(case))
                self.assertEqual(f".{expected}", utils.ext(case, leading_dot=True))
        # Edge case
        self.assertEqual("", utils.ext("filename_with_no_ext", leading_dot=True))


class TestTestUtilities(TestCase):
    """Test the test utilities provided."""

    def test_MockResponse(self) -> None:
        """Test the MockResponse class."""
        with self.subTest("Test creating a MockResponse object."):
            code = 200
            json = {"_key", "_value"}
            obj = MockResponse(code, json)
            self.assertEqual(code, obj.status_code)
            self.assertEqual(json, obj.json())
            self.assertEqual(str(json), obj.text)
        with self.subTest("Test the `ok` property."):
            self.assertFalse(MockResponse(100).ok)
            self.assertTrue(MockResponse(200).ok)
            self.assertFalse(MockResponse(400).ok)


class TestEnvUtilities(TestCase):
    """Test the provided utilities to deal with environment variables."""

    def test__get_value(self) -> None:
        """Test the `_get_value` function."""
        key = "_key"
        value = "_value"
        with patch("core.utilities.env.ENV", {key: value}):
            retval = env._get_value(key)
            self.assertEqual(value, retval)

    def test__get_value_missing_key(self) -> None:
        """Test the `_get_value` function with a missing key."""
        key = "_key"
        with patch("core.utilities.env.ENV", {}):
            with self.assertRaises(KeyError):
                env._get_value(key)

    def test__get_value_missing_key_default(self) -> None:
        """Test the `_get_value` function with a missing key, when a default is provided."""
        key = "_key"
        default = "_value"
        with patch("core.utilities.env.ENV", {}):
            retval = env._get_value(key, default)
            self.assertEqual(default, retval)

    def test__get_value_empty_value_default(self) -> None:
        """Test the `_get_value` function with a key with an empty value, when a default is provided."""
        key = "_key"
        default = "_value"
        with patch("core.utilities.env.ENV", {key: ""}):
            retval = env._get_value(key, default)
            self.assertEqual(default, retval)

    def test_as_string(self) -> None:
        """Test the `as_string` function."""
        key = "_key"
        value = "_value"
        with patch("core.utilities.env.ENV", {key: value}):
            retval = env.as_string(key)
            self.assertIsInstance(retval, str)
            self.assertEqual(value, retval)

    def test_as_int(self) -> None:
        """Test the `as_int` function."""
        key = "_key"
        value = 1
        with patch("core.utilities.env.ENV", {key: str(value)}):
            retval = env.as_int(key)
            self.assertIsInstance(retval, int)
            self.assertEqual(value, retval)

    def test_as_list(self) -> None:
        """Test the `as_list` function."""
        key = "_key"
        value = ["_first", "_second", "_third"]
        with patch("core.utilities.env.ENV", {key: ",".join(value)}):
            retval = env.as_list(key)
            self.assertIsInstance(retval, list)
            self.assertEqual(value, retval)

    def test_as_list_missing_key_default(self) -> None:
        """Test the `as_list` function with a missing key, when a default is provided."""
        key = "_key"
        default = ["_first", "_second", "_third"]
        with patch("core.utilities.env.ENV", {}):
            retval = env.as_list(key, default)
            self.assertEqual(default, retval)

    def test_as_bool(self) -> None:
        """Test the `as_bool` function."""
        key = "_key"
        true_values = ["TRUE", "true", "tRuE", "1", "T", "t"]
        false_values = ["FALSE", "false", "fAlSe", "f", "F", "0"]
        # Test for true values
        for value in true_values:
            with self.subTest(msg="True Values", value=value), patch("core.utilities.env.ENV", {key: str(value)}):
                retval = env.as_bool(key)
                self.assertIsInstance(retval, bool)
                self.assertEqual(True, retval)
        for value in false_values:
            with self.subTest(msg="False Values", value=value), patch("core.utilities.env.ENV", {key: str(value)}):
                retval = env.as_bool(key)
                self.assertIsInstance(retval, bool)
                self.assertEqual(False, retval)

    def test_as_bool_missing_key_default(self) -> None:
        """Test the `as_bool` function with a missing key, when a default is provided."""
        key = "_key"
        default = True
        with patch("core.utilities.env.ENV", {}):
            retval = env.as_bool(key, default)
            self.assertEqual(default, retval)

    def test_as_json(self) -> None:
        """Test the `as_json` function."""
        key = "_key"
        value = {"_key": "_value"}
        with patch("core.utilities.env.ENV", {key: json.dumps(value)}):
            retval = env.as_json(key)
            self.assertIsInstance(retval, dict)
            self.assertEqual(value, retval)

    def test_as_json_missing_key_default(self) -> None:
        """Test the `as_json` function with a missing key, when a default is provided."""
        key = "_key"
        default = {"_key": "_value"}
        with patch("core.utilities.env.ENV", {}):
            retval = env.as_json(key, default)
            self.assertIsInstance(retval, dict)
            self.assertEqual(default, retval)


class TestLoggingBuilder(TestCase):
    """Test the logging builder provided."""

    def test_add_formatter(self) -> None:
        """Test the `add_formatter` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        format = "_format"
        style = "_style"
        kwarg = "_kwarg"
        retval = builder.add_formatter(name, format, style, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual({"format": format, "style": style, "kwarg": kwarg}, built["formatters"][name])

    def test_set_default_formatter(self) -> None:
        """Test the `set_default_formatter` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        builder.add_formatter(name, "_format", "_style")
        retval = builder.set_default_formatter(name)
        self.assertEqual(retval, builder)  # Builder returned itself
        self.assertEqual(name, builder._default_formatter)
        # Attempt to add a handler
        handler_name = "_handler_name"
        builder.add_handler(handler_name)
        built = builder.build()
        self.assertEqual(name, built["handlers"][handler_name]["formatter"])

    def test_set_default_formatter_overridden(self) -> None:
        """Test the default formatter can be overridden by passing the formatter when adding the handler."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        builder.add_formatter(name, "_format", "_style")
        builder.set_default_formatter(name)
        # Attempt to add a handler
        handler_name = "_handler_name"
        formatter_name = "_formatter_name"
        builder.add_handler(handler_name, formatter=formatter_name)
        built = builder.build()
        self.assertEqual(formatter_name, built["handlers"][handler_name]["formatter"])

    def test_set_default_formatter_missing_fails(self) -> None:
        """Test the `set_default_formatter` method fails if the formatter name passed does not exist."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        with self.assertRaises(ValueError) as ctx:
            builder.set_default_formatter(name)
        self.assertEqual(f"No formatter named {name} added.", str(ctx.exception))
        self.assertIsNone(builder._default_formatter)

    def test_add_filter(self) -> None:
        """Test the `add_filter` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        filter = "_filter"
        kwarg = "_kwarg"
        retval = builder.add_filter(name, filter, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual({"()": filter, "kwarg": kwarg}, built["filters"][name])

    def test_add_handler(self) -> None:
        """Test the `add_handler` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        kwarg = "_kwarg"
        retval = builder.add_handler(name, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual({"kwarg": kwarg}, built["handlers"][name])

    def test_add_console_handler(self) -> None:
        """Test the `add_console_handler` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        kwarg = "_kwarg"
        retval = builder.add_console_handler(name, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual({"class": "logging.StreamHandler", "kwarg": kwarg}, built["handlers"][name])

    @patch("pathlib.Path.mkdir")
    def test_add_file_handler(self, mkdir_mock: MagicMock) -> None:
        """Test the `add_file_handler` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        file_path = utils.uuid()
        kwarg = "_kwarg"
        retval = builder.add_file_handler(name, file_path, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual(
            {"class": "logging.FileHandler", "filename": file_path, "kwarg": kwarg}, built["handlers"][name]
        )
        # Make sure the mock was called correctly
        mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)

    def test_add_logger(self) -> None:
        """Test the `add_logger` method."""
        builder = LoggingConfigurationBuilder()
        name = "_name"
        handlers = ["_handler1", "_handler2"]
        kwarg = "_kwarg"
        retval = builder.add_logger(name, handlers, kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual({"handlers": handlers, "kwarg": kwarg}, built["loggers"][name])

    def test_modify_root_logger(self) -> None:
        """Test the `modify_root_logger` method."""
        builder = LoggingConfigurationBuilder()
        kwarg = "_kwarg"
        retval = builder.modify_root_logger(kwarg=kwarg)
        self.assertEqual(retval, builder)  # Builder returned itself
        built = builder.build()
        self.assertEqual(kwarg, built["root"]["kwarg"])

    def test_build(self) -> None:
        """Test building an "empty" logger."""
        disable_existing = True
        builder = LoggingConfigurationBuilder(disable_existing)
        built = builder.build()
        self.assertEqual(
            {
                "version": 1,
                "disable_existing_loggers": disable_existing,
                "formatters": {},
                "filters": {},
                "handlers": {},
                "root": {},
                "loggers": {},
            },
            built,
        )
