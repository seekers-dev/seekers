# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import seekers_pb2 as seekers__pb2


class SeekersStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.JoinSession = channel.unary_unary(
                '/world.Seekers/JoinSession',
                request_serializer=seekers__pb2.SessionRequest.SerializeToString,
                response_deserializer=seekers__pb2.SessionReply.FromString,
                )
        self.PropertiesInfo = channel.unary_unary(
                '/world.Seekers/PropertiesInfo',
                request_serializer=seekers__pb2.PropertiesRequest.SerializeToString,
                response_deserializer=seekers__pb2.PropertiesReply.FromString,
                )
        self.EntityStatus = channel.unary_unary(
                '/world.Seekers/EntityStatus',
                request_serializer=seekers__pb2.EntityRequest.SerializeToString,
                response_deserializer=seekers__pb2.EntityReply.FromString,
                )
        self.PlayerStatus = channel.unary_unary(
                '/world.Seekers/PlayerStatus',
                request_serializer=seekers__pb2.PlayerRequest.SerializeToString,
                response_deserializer=seekers__pb2.PlayerReply.FromString,
                )
        self.CommandUnit = channel.unary_unary(
                '/world.Seekers/CommandUnit',
                request_serializer=seekers__pb2.CommandRequest.SerializeToString,
                response_deserializer=seekers__pb2.CommandReply.FromString,
                )


class SeekersServicer(object):
    """Missing associated documentation comment in .proto file."""

    def JoinSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PropertiesInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def EntityStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PlayerStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CommandUnit(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SeekersServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'JoinSession': grpc.unary_unary_rpc_method_handler(
                    servicer.JoinSession,
                    request_deserializer=seekers__pb2.SessionRequest.FromString,
                    response_serializer=seekers__pb2.SessionReply.SerializeToString,
            ),
            'PropertiesInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.PropertiesInfo,
                    request_deserializer=seekers__pb2.PropertiesRequest.FromString,
                    response_serializer=seekers__pb2.PropertiesReply.SerializeToString,
            ),
            'EntityStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.EntityStatus,
                    request_deserializer=seekers__pb2.EntityRequest.FromString,
                    response_serializer=seekers__pb2.EntityReply.SerializeToString,
            ),
            'PlayerStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.PlayerStatus,
                    request_deserializer=seekers__pb2.PlayerRequest.FromString,
                    response_serializer=seekers__pb2.PlayerReply.SerializeToString,
            ),
            'CommandUnit': grpc.unary_unary_rpc_method_handler(
                    servicer.CommandUnit,
                    request_deserializer=seekers__pb2.CommandRequest.FromString,
                    response_serializer=seekers__pb2.CommandReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'world.Seekers', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Seekers(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def JoinSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/world.Seekers/JoinSession',
            seekers__pb2.SessionRequest.SerializeToString,
            seekers__pb2.SessionReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PropertiesInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/world.Seekers/PropertiesInfo',
            seekers__pb2.PropertiesRequest.SerializeToString,
            seekers__pb2.PropertiesReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def EntityStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/world.Seekers/EntityStatus',
            seekers__pb2.EntityRequest.SerializeToString,
            seekers__pb2.EntityReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PlayerStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/world.Seekers/PlayerStatus',
            seekers__pb2.PlayerRequest.SerializeToString,
            seekers__pb2.PlayerReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CommandUnit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/world.Seekers/CommandUnit',
            seekers__pb2.CommandRequest.SerializeToString,
            seekers__pb2.CommandReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
