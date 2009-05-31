# vim: fileencoding=utf-8

from GoogleReader import GoogleReader, CONST

from const import CONF

def cache(key):
  def decorator(fn):
    def wrapper(self, *args, **kwargs):
      if not self.cache.has_key(key):
        self.cache[key] = fn(self, *args, **kwargs)
      return self.cache.get(key)
    return wrapper
  return decorator

class Reader(object):

  def __init__(self, email, password):
    self.reader = GoogleReader()
    self.reader.identify(email, password)
    if not self.reader.login():
      raise Exception(u'Failed to login to Google Reader')
    self.clear_cache()

  def clear_cache(self):
    self.cache = {}

  @cache('subscriptions')
  def get_subscriptions(self):
    subscriptions = {}
    for x in self.reader.get_subscription_list()['subscriptions']:
      subscriptions[x['id']] = x
    return subscriptions

  @cache('unread_feed')
  def get_unread_feed(self):
    return self.reader.get_feed(count=CONF.unread.max_count,
                                exclude_target=CONST.ATOM_STATE_READ)

  @cache('unread_entries')
  def get_unread_entries(self):
    subscriptions = self.get_subscriptions()
    entries = []
    for entry in self.get_unread_feed().get_entries():
      id = entry['sources'].keys()[0]
      entry['subscription_id'] = id
      entry['subscription_title'] = subscriptions[id]['title']
      entry['pinned'] = False
      entry['stared'] = False # TODO
      unread = entry['categories']['user/-/state/com.google/fresh']
      entry['unread'] = unread=='fresh'
      entries.append(entry)
    return entries

  @cache('feed_title')
  def get_feed_title(self):
    return self.get_unread_feed().get_title()

  @cache('unread_counts')
  def get_unread_counts(self):
    counts = {}
    for x in self.reader.get_unread_count_list()['unreadcounts']:
      counts[x['id']] = x['count']
    return counts

  @cache('unread_count')
  def get_unread_count(self):
    for k,v in self.get_unread_counts().iteritems():
      if k.endswith('/state/com.google/reading-list'): return v
    return 0

  def set_read(self, entry):
    if not entry['unread']: return
    self.reader.set_read(entry['google_id'])
    entry['unread'] = False
    self.cache['unread_count'] -= 1

  def set_unread(self, entry):
    if entry['unread']: return
    self.reader.set_unread(entry['google_id'])
    entry['unread'] = True
    self.cache['unread_count'] += 1
