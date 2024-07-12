# Developing pymerlin

For pymerlin development, you'll need:
- Java 21 JDK
- python 3.9 or higher

Additional libraries:
- build (for packaging)
- twine (for publishing)
- pytest (for running tests)

## Building pymerlin.jar

```shell
cd java
./gradlew assemble
mv pymerlin/build/libs/pymerlin.jar ../pymerlin/_internal/jars
```

## Testing

All tests are located in the `tests` directory, and are defined using pytest.

As of writing, tests can only be run in your current environment - so first run `pip install .`, and then `pytest`.

Future aspiration: use `tox` to test on multiple versions of python.

Future aspiration: automated testing of tutorial snippets in docs