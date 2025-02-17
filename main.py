import json
import logging
import os
import os.path
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)


class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        directories = []
        arg = event.get_argument()
        logger.info('preferences %s' % json.dumps(extension.preferences))

        # get directories from preferences
        if extension.preferences.get('directory_list') is not None:
            directories = [x.strip() for x in extension.preferences['directory_list'].split(
                ',')]

            # giv user feedback if no directory has been specified
            if len(directories) == 0:
                items.append(ExtensionResultItem(icon='images/dir.png',
                                                 name="No directories specified",
                                                 description="Add them in settings->extensions->Directory opener->Directory list",
                                                 on_enter=ExtensionCustomAction("none", keep_app_open=True)))
                return RenderResultListAction(items)

        if arg is not None and len(arg) > 0:
            directories = [x for x in directories if arg.lower() in x.lower()]

        for directory in directories:
            # Split the directory entry into path and alias
            path, alias = directory.split("|") if "|" in directory else (directory, directory)

            # Replace tilde with home directory path
            path = os.path.expanduser(path)

            # Append the item with the alias
            items.append(ExtensionResultItem(icon='images/dir.png',
                                             name=f"Open {alias}",
                                             on_enter=ExtensionCustomAction(path, keep_app_open=False)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        if (data == 'none'):
            return HideWindowAction()

        root_dir = extension.preferences.get("root_dir")
        browser = extension.preferences.get("default_filebrowser")

        os.popen(f"{browser} {root_dir}{data}")


if __name__ == '__main__':
    DemoExtension().run()
