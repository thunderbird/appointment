# Testing

## Working with `pytest.mark.parametrize`

In the cases where you'd like to run a test multiple times with different data sets you should use the `@pytest.mark.parametrize` decorator.

By default `@pytest.mark.parametrize` doesn't allow you to provide other fixtures as test data. 
Instead, you'll need to return the fixture name and dynamically call it using `request.getfixturevalue(fixture_name_as_a_str)`. 
An example of this can be seen in test_calendar.py::get_calendar_factory and any tests that use it.
