"""Generated-client consumer against an in-process loopback gRPC service."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import grpc

import candidate_pb2 as pb
import candidate_pb2_grpc as rpc


class ProfileService(rpc.ProfileServiceServicer):
    def __init__(self) -> None:
        self.read_attempts = 0
        self.watch_attempts = 0
        self.slow_cancelled = threading.Event()
        self.stream_cancelled = threading.Event()

    def GetProfile(self, request: pb.GetProfileRequest, context: grpc.ServicerContext) -> pb.Profile:
        if not request.id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "id is required")
        if request.id == "slow":
            while context.is_active():
                time.sleep(0.005)
            self.slow_cancelled.set()
            return pb.Profile()
        if request.id == "retry":
            self.read_attempts += 1
            if self.read_attempts == 1:
                context.abort(grpc.StatusCode.UNAVAILABLE, "transient read failure")
        if request.id == "missing":
            context.abort(grpc.StatusCode.NOT_FOUND, "profile not found")
        result = pb.Profile(id=request.id)
        result.display_name = ""  # Explicitly present empty value.
        return result

    def WatchProfiles(self, request: pb.WatchProfilesRequest, context: grpc.ServicerContext):
        self.watch_attempts += 1
        if not request.id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "id is required")
        context.send_initial_metadata((("x-contract", "stream-started"),))
        if request.id == "partial":
            yield pb.ProfileUpdate(sequence=1, profile=pb.Profile(id="partial"))
            context.abort(grpc.StatusCode.UNAVAILABLE, "stream interrupted")
        if request.id == "cancel":
            yield pb.ProfileUpdate(sequence=1, profile=pb.Profile(id="cancel"))
            while context.is_active():
                time.sleep(0.005)
            self.stream_cancelled.set()
            return
        for sequence in range(1, 4):
            yield pb.ProfileUpdate(sequence=sequence, profile=pb.Profile(id=request.id))


def main() -> None:
    service = ProfileService()
    server = grpc.server(ThreadPoolExecutor(max_workers=4))
    rpc.add_ProfileServiceServicer_to_server(service, server)
    port = server.add_insecure_port("127.0.0.1:0")
    assert port > 0
    server.start()

    retry_policy = {
        "maxAttempts": 2,
        "initialBackoff": "0.01s",
        "maxBackoff": "0.01s",
        "backoffMultiplier": 1,
        "retryableStatusCodes": ["UNAVAILABLE"],
    }
    service_config = json.dumps({"methodConfig": [{
        "name": [{"service": "example.profile.v1.ProfileService", "method": "GetProfile"},
                 {"service": "example.profile.v1.ProfileService", "method": "WatchProfiles"}],
        "retryPolicy": retry_policy,
    }]})
    channel = grpc.insecure_channel(
        f"127.0.0.1:{port}",
        options=(("grpc.enable_retries", 1), ("grpc.service_config", service_config)),
    )
    stub = rpc.ProfileServiceStub(channel)
    try:
        legacy_env = os.environ.copy()
        legacy_env["PYTHONPATH"] = os.pathsep.join(
            [os.environ["RPC_V1_GENERATED"], str(Path(__file__).parent)]
        )
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("legacy_consumer.py")), str(port)],
            check=True,
            env=legacy_env,
        )

        profile = stub.GetProfile(pb.GetProfileRequest(id="alice"), timeout=1)
        assert profile.id == "alice" and profile.HasField("display_name")
        assert profile.display_name == ""

        retried = stub.GetProfile(pb.GetProfileRequest(id="retry"), timeout=1)
        assert retried.id == "retry" and service.read_attempts == 2

        for profile_id, expected in (("", grpc.StatusCode.INVALID_ARGUMENT),
                                     ("missing", grpc.StatusCode.NOT_FOUND)):
            try:
                stub.GetProfile(pb.GetProfileRequest(id=profile_id), timeout=1)
            except grpc.RpcError as error:
                assert error.code() == expected
            else:
                raise AssertionError(f"expected {expected}")

        try:
            stub.GetProfile(pb.GetProfileRequest(id="slow"), timeout=0.04)
        except grpc.RpcError as error:
            assert error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
        else:
            raise AssertionError("deadline was not enforced")
        assert service.slow_cancelled.wait(1), "server did not observe deadline cancellation"

        completed_call = stub.WatchProfiles(pb.WatchProfilesRequest(id="complete"), timeout=1)
        updates = list(completed_call)
        assert [item.sequence for item in updates] == [1, 2, 3]
        assert completed_call.code() == grpc.StatusCode.OK

        partial_call = stub.WatchProfiles(pb.WatchProfilesRequest(id="partial"), timeout=1)
        partial = []
        try:
            partial.extend(partial_call)
        except grpc.RpcError as error:
            assert error.code() == grpc.StatusCode.UNAVAILABLE
        else:
            raise AssertionError("mid-stream terminal failure was hidden")
        assert [item.sequence for item in partial] == [1]
        assert service.watch_attempts == 2, "committed stream unexpectedly replayed from the start"

        cancel_call = stub.WatchProfiles(pb.WatchProfilesRequest(id="cancel"), timeout=2)
        assert next(cancel_call).sequence == 1
        cancel_call.cancel()
        assert service.stream_cancelled.wait(1), "server did not observe stream cancellation"
    finally:
        channel.close()
        server.stop(0).wait(1)


if __name__ == "__main__":
    main()
