import pprint


def not_(fn):
    def n(*args, **kwargs):
        return not fn(*args, **kwargs)

    return n


pp = pprint.PrettyPrinter(indent=2)
