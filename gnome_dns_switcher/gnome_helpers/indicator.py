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
    indicator: appindicator.Indicator
    menu: Gtk.Menu
    notifications: List[Notify.Notification] = []

    def __init__(self, application_id: str):
        # noinspection PyArgumentList
        # Using appindicator.Indicator() results in SIGSEGV
        self.indicator = appindicator.Indicator.new(application_id, 'server',
                                                    appindicator.IndicatorCategory.COMMUNICATIONS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        Notify.init(application_id)
        self.menu = Gtk.Menu()

        # INIT
        self.init_indicator()

        self.add_menu_item('Quit', Gtk.main_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.menu.connect('destroy', self.__cleanup)
        Gtk.main()

    def init_indicator(self):
        raise NotImplementedError

    def add_menu_item(self, label: str, on_activate=None, *args):
        item = Gtk.MenuItem()
        item.set_label(label)
        if on_activate:
            item.connect('activate', lambda source, *a: on_activate(*a), *args)
        self.menu.append(item)
        return item

    def notify(self, title: str, message: str, icon: str = 'server'):
        self.__clear_notifications()
        n = Notify.Notification().new(title, message, icon)
        n.show()
        self.notifications.append(n)

    def __clear_notifications(self):
        for n in self.notifications:
            n.close()

    def __cleanup(self):
        self.__clear_notifications()
        Notify.uninit()
