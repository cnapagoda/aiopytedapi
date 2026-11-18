#!/bin/bash
# Regenerate src/aiopytedapi/_proto/tedapi_pb2.py and tedapi_pb2.pyi from
# tedapi.proto. This is the only way the generated files are made: never edit
# them by hand, never run a bare protoc.
#
# The generator is grpcio-tools 1.62.x (protoc 25, protobuf 4.25.x gencode).
# That gencode does not embed a runtime version check, so it loads on every
# protobuf runtime from the library's floor (4.25.1) up, including the newer
# protobuf Home Assistant ships. grpcio-tools 1.62.x has no wheels for
# Python 3.13+, so the generator runs on Python 3.12 or older.
#
# Usage:  bash tools/gen_proto.sh            (makes a throwaway venv in .gen/)
#         GEN_VENV=/path/to/venv bash tools/gen_proto.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${GEN_PY:-python3.12}"
VENV="${GEN_VENV:-.gen}"
if [ ! -x "$VENV/bin/python" ]; then
    "$PY" -m venv "$VENV"
    "$VENV/bin/pip" install -q -r tools/requirements-gen.txt
fi

"$VENV/bin/python" -m grpc_tools.protoc \
    -I src \
    --python_out=src \
    --pyi_out=src \
    src/aiopytedapi/_proto/tedapi.proto
echo "Generated src/aiopytedapi/_proto/tedapi_pb2.py and tedapi_pb2.pyi"
