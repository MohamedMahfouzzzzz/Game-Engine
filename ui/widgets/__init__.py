# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from ui.widgets.console_panel import ConsolePanel
from ui.widgets.file_browser import ProjectFileBrowserWidget
from ui.widgets.inspector import InspectorWidget
from ui.widgets.scene_tree import SceneTreeWidget
from ui.widgets.viewport import ViewportWidget

__all__ = ["ConsolePanel", "ProjectFileBrowserWidget", "SceneTreeWidget", "InspectorWidget", "ViewportWidget"]
