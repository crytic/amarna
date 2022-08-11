from unittest import TestCase
from amarna.amarna import Amarna
from amarna.command_line import (
    get_config_from_file,
    get_rule_names,
    parse_args,
)


class TestConfigFile(TestCase):
    def test_include_one_rule(self):
        args = parse_args(["--config", "tests/config/include_add.toml"])
        include, exclude, _ = get_config_from_file(args.config)

        rule_set_names = get_rule_names(
            ",".join(filter(None, (args.rules, include))),
            ",".join(filter(None, (args.exclude_rules, exclude))),
        )
        self.assertListEqual(rule_set_names, ["arithmetic-add"])

    def test_include_several_rule(self):
        args = parse_args(["--config", "tests/config/several_include_rules.toml"])
        include, exclude, _ = get_config_from_file(args.config)

        rule_set_names = get_rule_names(
            ",".join(filter(None, (args.rules, include))),
            ",".join(filter(None, (args.exclude_rules, exclude))),
        )
        included_rules = [
            "arithmetic-add",
            "dead-store",
            "arithmetic-div",
            "arithmetic-mul",
            "arithmetic-sub",
            "uninitialized-variable",
            "unknown-decorator",
            "unused-arguments",
            "unused-imports",
        ]
        self.assertEqual(len(set(rule_set_names)), len(rule_set_names))
        self.assertSetEqual(
            set(rule_set_names),
            set(included_rules),
        )

    def test_exclude_one_rule(self):
        args = parse_args(["--config", "tests/config/exclude_add.toml"])
        include, exclude, _ = get_config_from_file(args.config)

        rule_set_names = get_rule_names(
            ",".join(filter(None, (args.rules, include))),
            ",".join(filter(None, (args.exclude_rules, exclude))),
        )
        expected_rules = [rule for rule in Amarna.get_all_rule_names() if rule != "arithmetic-add"]
        self.assertEqual(len(set(expected_rules)), len(expected_rules))
        self.assertEqual(len(set(rule_set_names)), len(rule_set_names))
        self.assertSetEqual(set(rule_set_names), set(expected_rules))

    def test_exclude_several_rules(self):
        args = parse_args(["--config", "tests/config/several_exclude_rules.toml"])
        include, exclude, _ = get_config_from_file(args.config)

        rule_set_names = get_rule_names(
            ",".join(filter(None, (args.rules, include))),
            ",".join(filter(None, (args.exclude_rules, exclude))),
        )
        excluded_rules = [
            "arithmetic-add",
            "dead-store",
            "arithmetic-div",
            "arithmetic-mul",
            "arithmetic-sub",
            "uninitialized-variable",
            "unknown-decorator",
            "unused-arguments",
            "unused-imports",
        ]
        expected_rules = [
            rule for rule in Amarna.get_all_rule_names() if rule not in excluded_rules
        ]
        self.assertEqual(len(set(expected_rules)), len(expected_rules))
        self.assertEqual(len(set(rule_set_names)), len(rule_set_names))
        self.assertSetEqual(set(rule_set_names), set(expected_rules))

    def test_disable_inline(self):
        args = parse_args(["--config", "tests/config/disable_inline.toml"])
        *_, disable_inline = get_config_from_file(args.config)
        assert disable_inline

    def test_enable_inline(self):
        args = parse_args(["--config", "tests/config/enable_inline.toml"])
        *_, disable_inline = get_config_from_file(args.config)
        assert not disable_inline
