# vim: fileencoding=utf-8

import sys

from const import MODE

CALLBACKS = {
  MODE.UNREAD: {},
  MODE.BROWSE: {},
  MODE.STARED: {},
}

def execute(app, key):
  callback = CALLBACKS.get(app.mode).get(key)
  if callback:
    try:
      callback(app)
    except Exception, e:
      app.ui.command_line.err(e.message)

# decorator functions --------------------------------------------------------

def callback(mode, key):
  def decorator(fn):
    CALLBACKS[mode][key] = fn
    return fn
  return decorator

def confirm(message, defans=True):
  def decorator(fn):
    def wrapper(app):
      app.ui.command_line.confirm(message, lambda: fn(app), defans)
    return wrapper
  return decorator

def loading(fn):
  def wrapper(app):
    app.ui.command_line.loading(lambda: fn(app))
  return wrapper

def update_status(fn):
  def wrapper(app):
    fn(app)
    # TODO
    app.ui.status_line.update(app.reader.get_feed_title(),
                              0,#len(app.reader.pinned_entries),
                              0,
                              app.reader.get_unread_count())
  return wrapper


# callback functions ---------------------------------------------------------

@callback(MODE.UNREAD, 'q')
@confirm(u'Are you sure you want to quit?')
def quit(app):
  sys.exit()

@callback(MODE.BROWSE, 'u')
@loading
@update_status
def switch_unread_mode(app):
  app.mode = MODE.UNREAD
  app.ui.grid_panel.update(app.reader.get_unread_entries())

@callback(MODE.UNREAD, '\n')
@loading
@update_status
def switch_browse_mode(app):
  app.mode = MODE.BROWSE
  entry = app.reader.get_unread_entries()[app.ui.grid_panel.selected]
#  self.reader.set_read(entry)
  app.ui.browse_panel.update(entry)

@callback(MODE.UNREAD, 'j')
def next(app):
  return app.ui.grid_panel.next(app.reader.get_unread_entries())

@callback(MODE.UNREAD, 'k')
def prev(app):
  return app.ui.grid_panel.prev(app.reader.get_unread_entries())

@callback(MODE.BROWSE, 'j')
def next_browse(app):
  if next(app): switch_browse_mode(app)

@callback(MODE.BROWSE, 'k')
def prev_browse(app):
  if prev(app): switch_browse_mode(app)
