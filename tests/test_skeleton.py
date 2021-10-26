import pyro

from mypackage import MyModel


def test_mymodel():
    model = MyModel()

    # tests __repr__
    print(model)