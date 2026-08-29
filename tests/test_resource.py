from sunsynk.resource import to_float, to_int


def test_to_float():
    assert to_float('12.2') == 12.2
    assert to_float(5) == 5.0
    assert to_float(None) is None
    assert to_float('') is None
    assert to_float('abc') is None


def test_to_int():
    assert to_int('2') == 2
    assert to_int(3.0) == 3
    assert to_int(None) is None
    assert to_int('') is None
    assert to_int('abc') is None
