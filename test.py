import sys

sys.setrecursionlimit(10)
class Dataset(object):
    def __getattr__(self, item):
        if not item in dir(self):
            print(item)

    @property
    def index(self):
        return 1

a = Dataset()
print(a.index)