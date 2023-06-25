from typing import List

import gi

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

gi.require_version("GLib", "2.0")

gi.require_version('Notify', '0.7')
from gi.repository import Notify


class Indicator:
    _return_code: int = 0
    _application_id: str
    _indicator: appindicator.Indicator = None
    _menu: Gtk.Menu = None
    _notifications: List[Notify.Notification] = []

    def __init__(self, application_id: str):
        self._application_id = application_id

    def open(self):
        if self._indicator:
            raise AssertionError('Already open')

        self._indicator = appindicator.Indicator.new(
            self._application_id,
            'server',
            appindicator.IndicatorCategory.COMMUNICATIONS,
        )
        self._indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        Notify.init(self._application_id)
        self._menu = Gtk.Menu()

        # Allow child implementation to set up its menu
        self.init_indicator()

        self.add_menu_item('Quit', Gtk.main_quit)
        self._menu.show_all()
        self._indicator.set_menu(self._menu)

        self._menu.connect('destroy', self.__cleanup)  # This doesn't trigger when we quit ourselves
        Gtk.main()
        self.__cleanup()
        return self._return_code

    def init_indicator(self):
        raise NotImplementedError

    def add_menu_item(self, label: str, on_activate=None, *args):
        item = Gtk.MenuItem.new_with_label(label)

        if on_activate:
            item.connect('activate', lambda source, *a: on_activate(*a), *args)
        self._menu.append(item)

    def add_separator(self):
        self._menu.append(Gtk.SeparatorMenuItem.new())

    def set_label(self, label: str):
        self._indicator.set_label(label, label)

    def notify(self, title: str, message: str, icon: str = 'server'):
        self.__clear_notifications()
        n = Notify.Notification().new(title, message, icon)
        n.show()
        self._notifications.append(n)

    def close(self, return_code: int = 0):
        self._return_code = return_code
        Gtk.main_quit()

    def __clear_notifications(self):
        for n in self._notifications:
            n.close()

    def __cleanup(self):
        self._indicator.run_dispose()
        self.__clear_notifications()
        Notify.uninit()
