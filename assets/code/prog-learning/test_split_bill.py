from hypothesis import given, strategies as s
from split_bill import split_bill

# the kind of tests that come back with the function
def test_even_split():
    assert split_bill(90, 3) == [30.0, 30.0, 30.0]

def test_two_people():
    assert split_bill(50, 2) == [25.0, 25.0]

# the invariant nobody wrote down: the shares add up to the bill, to the cent
@given(cents=s.integers(1, 100_000), people=s.integers(1, 20))
def test_shares_add_up(cents, people):
    shares = split_bill(cents / 100, people)
    assert round(sum(shares) * 100) == cents
