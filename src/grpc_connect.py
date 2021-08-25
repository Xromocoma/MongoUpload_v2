import grpc
from skyproto_pb import media_pb2_grpc

from config import UPLOAD_GRPC_ADDRESS

# channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS)