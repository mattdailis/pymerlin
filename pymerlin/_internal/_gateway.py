"""
The gateway module is responsible for orchestrating all communication to Java

Open question whether any java objects should be allowed to leak outside of this class, or if they should be
totally encapsulated. TODO Investigate what pyspark does.
"""

import subprocess
from contextlib import contextmanager

from py4j.java_gateway import JavaGateway, CallbackServerParameters, GatewayParameters


@contextmanager
def start_gateway(jar_path, java_executable='java'):
    process = subprocess.Popen(
        [java_executable, '-jar', jar_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdout.readline()  # wait for server to be ready
    try:
        gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True),
                              callback_server_parameters=CallbackServerParameters())
        try:
            yield gateway
        finally:
            gateway.close()
            gateway.shutdown()
    finally:
        for line in process.stdout:
            print(line.decode(), end='')
        for line in process.stderr:
            print(line.decode(), end='')
        process.terminate()