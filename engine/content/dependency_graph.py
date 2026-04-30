# /**************************************************************************/
# /*  dependency_graph.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from collections import defaultdict
from typing import DefaultDict, List, Set

import logging


logger = logging.getLogger(__name__)



class AssetDependencyGraph:
    def __init__(self) -> None:
        self._deps: DefaultDict[str, Set[str]] = defaultdict(set)

    def add_dependency(self, asset: str, depends_on: str) -> None:
        self._deps[asset].add(depends_on)

    def get_dependencies(self, asset: str) -> List[str]:
        return sorted(self._deps.get(asset, set()))
