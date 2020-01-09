from mo3jam.grpc_services.search.search_pb2_grpc import SearchServicer
from mo3jam.grpc_services.search.search_pb2 import SearchResultSet, SearchResult

class Searcher(SearchServicer):
    def search(self, request, context):
        print('server recieved %s' % request.query)
        results = [SearchResult(match='a')]
        return SearchResultSet(results=results)

    def autocomplete(self, request, context):
        pass



