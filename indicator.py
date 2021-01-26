import gi

gi.require_version('AppIndicator3', '0.1')
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk
from gi.repository import Notify as notify


class Indicator:
    def __init__(self, APPINDICATOR_ID):
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'server',
                                                    appindicator.IndicatorCategory.COMMUNICATIONS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu = gtk.Menu()

        # INIT
        self.init_indicator()

        self.add_menu_item('Quit', self.quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        notify.init(APPINDICATOR_ID)
        gtk.main()

    def init_indicator(self):
        raise NotImplementedError

    def add_menu_item(self, label: str, on_activate=None, *args):
        item = gtk.MenuItem()
        item.set_label(label)
        if on_activate:
            item.connect('activate', self.__wrap_callback_func(on_activate), *args)
        self.menu.append(item)
        return item

    def notify(self, title: str, message: str):
        notify.Notification.new(title, message, None).show()

    def quit(self):
        notify.uninit()
        gtk.main_quit()

    def __wrap_callback_func(self, callback):
        def c(source, *args):
            callback(*args)

        return c
