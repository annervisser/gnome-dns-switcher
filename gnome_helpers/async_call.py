import threading

import gi

gi.require_version('GLib', '2.0')
from gi.repository import GLib


# FROM https://gist.github.com/diosmosis/1132418
def async_call(f, on_done=lambda r, e: None):
    def do_call():
        result = error = None
        try:
            result = f()
        except Exception as err:
            error = err

        GLib.idle_add(lambda: on_done(result, error))

    threading.Thread(target=do_call).start()
