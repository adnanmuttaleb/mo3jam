from concurrent import futures
import logging
import grpc


class Server():

    def __init__(self, *args, **kwargs):
        self._server = None
        super().__init__(*args, **kwargs)

    def serve(self, port=50051):
        self._server.add_insecure_port('[::]:%s' % port)
        self._server.start()
        self._server.wait_for_termination()

    def initialize(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    def add_service(self, service, registrator):
        registrator(service, self._server)

