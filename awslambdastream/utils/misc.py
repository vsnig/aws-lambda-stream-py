def not_(fn):
  def n(*args, **kwargs):
    return not fn(*args, **kwargs)
  return n