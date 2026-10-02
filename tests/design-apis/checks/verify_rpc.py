#!/usr/bin/env python3
"""Compile and execute RPC/Proto design fixtures in an isolated environment."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


TOOLS_VERSION = "1.84.0"
PROTOBUF_VERSION = "7.36.2"


def run(
    label: str,
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["rtk", "proxy", *command], cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            f"{label} failed ({result.returncode})\n{result.stdout}\n{result.stderr}"
        )
    return result


def compile_proto(python: Path, proto: Path, output: Path) -> None:
    output.mkdir(parents=True)
    result = run(
        f"protoc {proto.name}",
        [
            str(python), "-m", "grpc_tools.protoc",
            f"--proto_path={proto.parent}",
            f"--python_out={output}",
            f"--grpc_python_out={output}",
            str(proto),
        ],
    )
    if result.stdout or result.stderr:
        print((result.stdout + result.stderr).strip())


def verify_schema(python: Path, fixtures: Path, generated: Path) -> None:
    script = r'''
import ast
from pathlib import Path
import sys
from google.protobuf import descriptor_pb2, descriptor_pool, json_format, message_factory
sys.path[:0] = sys.argv[1:4]

def generated_profile(directory, module_name):
    tree = ast.parse((Path(directory) / f"{module_name}_pb2.py").read_text())
    serialized = next(
        ast.literal_eval(node.args[0])
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "AddSerializedFile"
    )
    descriptor = descriptor_pb2.FileDescriptorProto.FromString(serialized)
    pool = descriptor_pool.DescriptorPool()
    pool.Add(descriptor)
    message = message_factory.GetMessageClass(
        pool.FindMessageTypeByName("example.profile.v1.Profile")
    )
    return message, descriptor

def removed_field_errors(old_descriptor, new_descriptor):
    old_profile = next(m for m in old_descriptor.message_type if m.name == "Profile")
    new_profile = next(m for m in new_descriptor.message_type if m.name == "Profile")
    new_by_number = {field.number: field for field in new_profile.field}
    new_by_name = {field.name: field for field in new_profile.field}
    reserved_numbers = {
        number
        for reserved in new_profile.reserved_range
        for number in range(reserved.start, reserved.end)
    }
    reserved_names = set(new_profile.reserved_name)
    errors = []
    for old_field in old_profile.field:
        same_identity = new_by_number.get(old_field.number)
        if same_identity and same_identity.name != old_field.name:
            errors.append(
                f"tag {old_field.number} changed from {old_field.name} to {same_identity.name}"
            )
        elif same_identity and same_identity.type != old_field.type:
            errors.append(f"field {old_field.name}#{old_field.number} changed type")
        elif not same_identity and old_field.number not in reserved_numbers:
            errors.append(f"deleted field number {old_field.number} is not reserved")
        if old_field.name not in new_by_name and old_field.name not in reserved_names:
            errors.append(f"deleted field name {old_field.name} is not reserved")
    return errors

old, _old_file = generated_profile(sys.argv[1], "v1")
new, candidate_file = generated_profile(sys.argv[2], "candidate")
broken, _broken_file = generated_profile(sys.argv[3], "broken")
assert removed_field_errors(_old_file, candidate_file) == []
unsafe_errors = removed_field_errors(_old_file, _broken_file)
assert unsafe_errors == [
    "tag 2 changed from legacy_name to display_name",
    "deleted field name legacy_name is not reserved",
], unsafe_errors

old_wire = old(id="p1", legacy_name="old name").SerializeToString()
new_from_old = new.FromString(old_wire)
assert new_from_old.id == "p1"
assert not new_from_old.HasField("display_name")
assert new_from_old.display_name == ""
assert new_from_old.SerializeToString() == old_wire, "runtime did not preserve the unknown old field"

new_wire = new(id="p2", display_name="new name").SerializeToString()
old_from_new = old.FromString(new_wire)
assert old_from_new.id == "p2" and old_from_new.legacy_name == ""

explicit_zero = new(id="p3", display_name="", reputation=0)
assert explicit_zero.HasField("display_name") and explicit_zero.HasField("reputation")
json_text = json_format.MessageToJson(explicit_zero)
assert '"displayName": ""' in json_text and '"reputation": 0' in json_text
round_trip = new()
json_format.Parse(json_text, round_trip)
assert round_trip.HasField("display_name") and round_trip.display_name == ""
assert round_trip.HasField("reputation") and round_trip.reputation == 0
try:
    json_format.Parse('{"displayName":"new"}', old())
except json_format.ParseError:
    pass
else:
    raise AssertionError("old ProtoJSON parser accepted an unknown field by default")
ignored = old()
json_format.Parse('{"displayName":"new"}', ignored, ignore_unknown_fields=True)
assert ignored.legacy_name == "", "ignore-unknown must report/acknowledge information loss"

profile_desc = next(m for m in candidate_file.message_type if m.name == "Profile")
assert any(r.start == 2 and r.end == 3 for r in profile_desc.reserved_range)
assert "legacy_name" in profile_desc.reserved_name

# protoc compiles this deliberately unsafe schema; the same descriptor-level
# checker used for the candidate must reject its reused tag.
old_field_numbers = {f.number for f in old.DESCRIPTOR.fields}
unsafe_numbers = {f.number for f in broken.DESCRIPTOR.fields}
assert 2 in old_field_numbers and 2 in unsafe_numbers
unsafe_reuse = next(f for f in broken.DESCRIPTOR.fields if f.number == 2)
assert unsafe_reuse.name == "display_name"
print("PASS generated descriptors, binary evolution, ProtoJSON, presence, tag-reuse negative")
'''
    result = run(
        "Proto compatibility consumer",
        [
            str(python), "-c", script,
            str(generated / "v1"),
            str(generated / "candidate"),
            str(generated / "broken"),
        ],
    )
    print(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "rpc-profile",
        help="RPC fixture directory (defaults to tests/design-apis/cases/rpc-profile)",
    )
    args = parser.parse_args()
    fixtures = args.fixtures.resolve()
    required = ("v1.proto", "candidate.proto", "broken.proto", "consumer.py", "legacy_consumer.py")
    missing = [name for name in required if not (fixtures / name).is_file()]
    if missing:
        parser.error(f"fixture directory missing: {', '.join(missing)}")

    python = Path(sys.executable)
    with tempfile.TemporaryDirectory(prefix="coder-rpc-verify-") as temporary_name:
        temporary = Path(temporary_name)
        env_dir = temporary / "venv"
        run("isolated Python environment", [str(python), "-m", "venv", str(env_dir)])
        bin_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
        env_python = bin_dir / ("python.exe" if os.name == "nt" else "python")
        run(
            "pinned RPC toolchain install",
            [
                str(env_python), "-m", "pip", "install", "--disable-pip-version-check",
                f"grpcio=={TOOLS_VERSION}",
                f"grpcio-tools=={TOOLS_VERSION}",
                f"protobuf=={PROTOBUF_VERSION}",
            ],
        )
        protoc_version = run(
            "protoc version", [str(env_python), "-m", "grpc_tools.protoc", "--version"]
        ).stdout.strip()
        generated = temporary / "generated"
        for name in ("v1", "candidate", "broken"):
            output = generated / name
            compile_proto(env_python, fixtures / f"{name}.proto", output)
        verify_schema(env_python, fixtures, generated)
        consumer_env = os.environ.copy()
        consumer_env["PYTHONPATH"] = os.pathsep.join(
            [str(generated / "candidate"), str(fixtures), consumer_env.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)
        consumer_env["RPC_V1_GENERATED"] = str(generated / "v1")
        consumer_result = run(
            "generated gRPC loopback consumer",
            [str(env_python), str(fixtures / "consumer.py")],
            cwd=fixtures,
            env=consumer_env,
        )
        print(consumer_result.stdout.strip())
        print(
            "PASS protoc compile/generation (v1,candidate,broken); "
            "PASS generated gRPC loopback unary/stream/deadline/retry/cancel"
        )
        print(
            f"Toolchain: grpcio=={TOOLS_VERSION}, grpcio-tools=={TOOLS_VERSION}, "
            f"protobuf=={PROTOBUF_VERSION}, {protoc_version} (temporary venv)"
        )


if __name__ == "__main__":
    main()
