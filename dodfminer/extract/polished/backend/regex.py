"""Regex backend for act and propriety extraction.

This module contains the ActRegex class, which have all that is necessary to
extract an act and, its proprieties, using regex rules.

"""

import re


class ActRegex:
    """Act Regex Class.

    This class encapsulate all functions, and attributes related
    to the process of regex extraction.

    Note:
        This class is one of the fathers of the Base act class.

    Attributes:
        _flags: All the regex flags which will be used in extraction.
        _rules: The regex rules for proprieties extraction.
        _inst_rule: The regex rule for act extraction.

    """

    def __init__(self):
        super(ActRegex, self).__init__()
        self._flags = self._regex_flags()
        self._rules = self._prop_rules()
        self._inst_rule = self._rule_for_inst()

    def _rule_for_inst(self):
        """Rule for extraction of the act

        Warning:
            Must return a regex rule that finds an act in two parts,
            containing a head and a body. Where only the body will be used
            to search for proprieties.

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _prop_rules(self):
        """Rules for extraction of the proprieties.

        Must return a dictionary of regex rules, where the key is
        the propriety type and the value is the rule.

        Raises:
            NotImplementedError: Child class needs to overwrite this method

        """
        raise NotImplementedError

    def _regex_flags(self):
        """Flag of the regex search"""
        return 0

    def _regex_instances(self):
        """Search for all instances of the act using the defined rule.

        Returns:
            List of all act instances in the text.
        """
        found = re.findall(self._inst_rule, self._text, flags=self._flags)
        results = []
        for instance in found:
            head, body = instance
            self.acts_str.append(head+body)
            results.append(body)

        return results

    def _find_prop_value(self, rule, act):
        """Find a single proprietie in an single act.

        Args:
            rule (str): The regex rule to search for.
            act (str): The act to apply the rule.

        Returns:
            The found propriety, or a nan in case nothing is found.

        """
        match = re.search(rule, act, flags=self._flags)
        if match:
            return tuple(x for x in match.groups() if x is not None)
        return "nan"

    def _regex_props(self, act_raw):
        """Create an act dict with all its proprieties.

        Args:
            act_raw (str): The raw text of a single act.

        Returns:
            The act, and its props in a dictionary format.

        """
        act = {}
        act["tipo_ato"] = self._name
        for key in self._rules:
            try:
                act[key], = self._find_prop_value(self._rules[key], act_raw)
            except Exception:
                act[key] = "nan"

        return act

    def _extract_instances(self):
        """Extract instances of an act.

        Warning:
            Instance must have an head and an body.

        Returns:
            All the instances of the act found.

        """
        found = self._find_instances()
        results = []
        for instance in found:
            head, body = instance
            self.acts_str.append(head+body)
            results.append(body)

        return results
