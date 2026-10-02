"""Old generated client call against the candidate server over loopback."""

from __future__ import annotations

import sys

import grpc

import v1_pb2 as old_pb
import v1_pb2_grpc as old_rpc


def main() -> None:
    channel = grpc.insecure_channel(f"127.0.0.1:{sys.argv[1]}")
    try:
        stub = old_rpc.ProfileServiceStub(channel)
        response = stub.GetProfile(old_pb.GetProfileRequest(id="legacy-client"), timeout=1)
        assert response.id == "legacy-client"
        assert response.legacy_name == ""  # Candidate-only field 3 is unknown to v1.
        print("PASS generated v1 client call against candidate service")
    finally:
        channel.close()


if __name__ == "__main__":
    main()
