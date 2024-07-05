# Architecture

pymerlin is to merlin as [pyspark](https://spark.apache.org/docs/latest/api/python/index.html) is to [spark](https://spark.apache.org/).
This means that pymerlin uses [py4j](https://www.py4j.org/) as a bridge
between a python process and a java process. This allows pymerlin to use the Aerie simulation engine directly, without
having to re-implement it in python.

This means that running `simulate` starts a subprocess using `java -jar /path/to/pymerlin.jar`.

## Approachability over performance

The main tenet of pymerlin is approachability, and its aim is to enable rapid prototyping of models and activities.
While where possible, performance will be considered, it is expected that someone who wants to seriously engineer the
performance of their simulation will port their code to Java - which has the double benefit of removing socket
communication overhead, as well as giving the engineer a single Java process to instrument and analyze, rather than a
hybrid system, which may be more difficult to characterize.