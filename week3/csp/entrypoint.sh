#!/bin/bash
cd /app/libcsp
python3 ./examples/buildall.py
./build/zmqproxy &
LD_LIBRARY_PATH=build PYTHONPATH=build python3 examples/python_bindings_example_server.py &
LD_LIBRARY_PATH=build PYTHONPATH=build python3 examples/python_bindings_example_client.py -z localhost

cd /app/parser
make test

chmod 600 /root/.ssh/authorized_keys
chown root:root /root/.ssh/authorized_keys
exec /usr/sbin/sshd -D