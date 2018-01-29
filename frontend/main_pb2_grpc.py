# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import main_pb2 as main__pb2


class TerminalBackendStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetState = channel.unary_unary(
        '/zischr.rpc.TerminalBackend/GetState',
        request_serializer=main__pb2.TerminalStateRequest.SerializeToString,
        response_deserializer=main__pb2.TerminalStateResponse.FromString,
        )
    self.Buy = channel.unary_unary(
        '/zischr.rpc.TerminalBackend/Buy',
        request_serializer=main__pb2.TerminalBuyRequest.SerializeToString,
        response_deserializer=main__pb2.TerminalBuyResponse.FromString,
        )
    self.AddDepositOrder = channel.unary_unary(
        '/zischr.rpc.TerminalBackend/AddDepositOrder',
        request_serializer=main__pb2.TerminalAddDepositOrderRequest.SerializeToString,
        response_deserializer=main__pb2.TerminalAddDepositOrderResponse.FromString,
        )
    self.Scan = channel.unary_unary(
        '/zischr.rpc.TerminalBackend/Scan',
        request_serializer=main__pb2.TerminalScanRequest.SerializeToString,
        response_deserializer=main__pb2.TerminalScanResponse.FromString,
        )
    self.Abort = channel.unary_unary(
        '/zischr.rpc.TerminalBackend/Abort',
        request_serializer=main__pb2.AbortRequest.SerializeToString,
        response_deserializer=main__pb2.AbortResponse.FromString,
        )


class TerminalBackendServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetState(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Buy(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def AddDepositOrder(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Scan(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Abort(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TerminalBackendServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetState': grpc.unary_unary_rpc_method_handler(
          servicer.GetState,
          request_deserializer=main__pb2.TerminalStateRequest.FromString,
          response_serializer=main__pb2.TerminalStateResponse.SerializeToString,
      ),
      'Buy': grpc.unary_unary_rpc_method_handler(
          servicer.Buy,
          request_deserializer=main__pb2.TerminalBuyRequest.FromString,
          response_serializer=main__pb2.TerminalBuyResponse.SerializeToString,
      ),
      'AddDepositOrder': grpc.unary_unary_rpc_method_handler(
          servicer.AddDepositOrder,
          request_deserializer=main__pb2.TerminalAddDepositOrderRequest.FromString,
          response_serializer=main__pb2.TerminalAddDepositOrderResponse.SerializeToString,
      ),
      'Scan': grpc.unary_unary_rpc_method_handler(
          servicer.Scan,
          request_deserializer=main__pb2.TerminalScanRequest.FromString,
          response_serializer=main__pb2.TerminalScanResponse.SerializeToString,
      ),
      'Abort': grpc.unary_unary_rpc_method_handler(
          servicer.Abort,
          request_deserializer=main__pb2.AbortRequest.FromString,
          response_serializer=main__pb2.AbortResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'zischr.rpc.TerminalBackend', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
