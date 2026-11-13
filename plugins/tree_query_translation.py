"""Tree query translation plugin based on CQP/Tree (https://github.com/Niklas-Deworetzki/cqp-tree).

Enable with PLUGINS=["plugins.tree_query_translation"].
"""

import re
from collections.abc import Mapping
from typing import Any
from pathlib import Path

from cqp_tree import translate as tree_translate, configuration_from_file, known_translators
from cqp_tree.translation import InputError, ParsingFailed, NotSupported, UnableToGuessTranslatorError

from korp.dependencies import Ctx

class TreeQueryTranslator:
    """Tree query translator supporting Grew, dep_search, deptreepy and more.

    Korp shares this instance across concurrent requests. Keep per-query parser and compilation state local to
    each call, and treat any configuration stored on the instance as read-only during translation.
    """

    languages =  frozenset(known_translators.keys())
    cqptree_config = configuration_from_file(Path("/home/harisont/Repos/Niklas-Deworetzki/cqp-tree/configurations/spraakbanken-korp/server.toml"))

    async def translate(self, ctx: Ctx, language: str, query: str) -> str:  # ruff: ignore[no-self-use, unused-method-argument]
        """Translate a tree query in one of the languages supported by CQP/Tree into a CQP expression.

        Returns:
            One CQP expression.

        Raises:
            ValueError: If the input cannot be parsed in any of the languages supported by CQP/Tree.
        """

        try: 
            translation = tree_translate(str, self.cqptree_config, prohibit_recipes=True)[-1]
        except Exception as error:
            raise ValueError("{}".format(error))

        # Return one non-empty CQP expression without a trailing semicolon or outer within clause.
        return translation


def create_translator(config: Mapping[str, Any]) -> TreeQueryTranslator:  # ruff: ignore[unused-function-argument]
    """Create a query translator provider for this plugin.

    Korp calls this factory at app creation with this plugin's `PLUGINS_CONFIG` entry (or an empty mapping).
    Validate settings and initialize reusable library configuration here.

    Returns:
        The configured provider.
    """
    return TreeQueryTranslator()


QUERY_TRANSLATOR_FACTORY = create_translator

"""
TODO:

- decide where to store the CQP/Tree config (hardcoded right now)
- this still relies on manually installing CQP/Tree `uv pip install path/to/local/cqp-tree/`. Make it pip-installable with option for minimal dependencies?
- `cqp_tree.known_translators.keys()` makes it so that we can translate all languages supported by CQP/Tree, *including CoNLL-U*. Is that what we want?
- checke whether conversion takes longer than 50ms, move to a different thread if not
- lang useless right now because tree_translate guesses it, should we make it optional (here or in tree_translate)?
- exception handling is basic right now because apparently "catching classes that do not inherit from BaseException (like InputError, ParsingFailed, NotSupported, UnableToGuessTranslatorError) is not allowed""
"""
