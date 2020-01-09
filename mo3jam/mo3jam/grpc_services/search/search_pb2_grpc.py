# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from mo3jam.grpc_services.search import search_pb2 as mo3jam_dot_grpc__services_dot_search_dot_search__pb2


class SearchStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.search = channel.unary_unary(
        '/Search/search',
        request_serializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchQuery.SerializeToString,
        response_deserializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchResultSet.FromString,
        )
    self.autocomplete = channel.unary_unary(
        '/Search/autocomplete',
        request_serializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchQuery.SerializeToString,
        response_deserializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.AutoCompleteResultSet.FromString,
        )


class SearchServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def search(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def autocomplete(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SearchServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'search': grpc.unary_unary_rpc_method_handler(
          servicer.search,
          request_deserializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchQuery.FromString,
          response_serializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchResultSet.SerializeToString,
      ),
      'autocomplete': grpc.unary_unary_rpc_method_handler(
          servicer.autocomplete,
          request_deserializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.SearchQuery.FromString,
          response_serializer=mo3jam_dot_grpc__services_dot_search_dot_search__pb2.AutoCompleteResultSet.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Search', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))