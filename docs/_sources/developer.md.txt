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