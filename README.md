# pymerlin

<!-- start elevator-pitch -->
pymerlin is a discrete event simulation framework, built for use in the [Aerie](https://github.com/NASA-AMMOS/aerie>) ecosystem.

To learn more about Aerie, read the [Aerie Docs](https://nasa-ammos.github.io/aerie-docs).
<!-- end elevator-pitch -->

### TODO:

- [ ] Daemon tasks
- [x] More interesting cells and resources
- [x] Conditions on static cells
- [x] Conditions on autonomous cells
- [x] Child tasks
- [ ] Spiceypy
- [ ] JPL time
- [ ] pip-installable models
- [ ] build Aerie-compatible jars and provide docker-compose file with python
- [ ] checkpoint restart

## Prerequisites

- python >=3.6.3 (only tested on 3.11 so far...)
- java >=21

Install pymerlin by running `pip install pymerlin`

1. Make a venv `python -m venv venv`
2. Activate the venv `source ./venv/bin/activate`
3. Install requirements `python -m pip install -r requirements.txt`
4. Start jupyter lab `jupyter-lab`
5. When jupyter opens, navigate to `demo/simulation_example.py`
6. Update the path in the first cell to point to your cloned `pymerlin` directory (we should eliminate the need for this
   hack)
7. Run all cells

## Architecture

pymerlin is to merlin as pyspark is to spark. This means that pymerlin uses [py4j](https://www.py4j.org/) as a bridge
between a python process and a java process. This allows pymerlin to use the Aerie simulation engine directly, without
having to re-implement it in python.

This means that running `simulate` starts a subprocess using `java -jar /path/to/pymerlin.jar`.

### Approachability over performance

The main tenet of pymerlin is approachability, and its aim is to enable rapid prototyping of models and activities.
While where possible, performance will be considered, it is expected that someone who wants to seriously engineer the
performance of their simulation will port their code to Java - which has the double benefit of removing socket
communication overhead, as well as giving the engineer a single Java process to instrument and analyze, rather than a
hybrid system, which may be more difficult to characterize.

## Building pymerlin.jar

If any changes are made to the java code, rebuild the jar and place it in the correct location as follows:

```shell
cd java
./gradlew assemble
mv pymerlin/build/libs/pymerlin.jar ../pymerlin/_internal/jars
```

The jar lives inside of the `pymerlin` python source directory because that ensures that it will be packaged
(and accessible) in a distribution.