from concurrent import futures #Allow to set no. of workers on server
import grpc
import locate_pb2
import locate_pb2_grpc

import extra_functions

class LocateService(locate_pb2_grpc.locateServicer):
    def getFilteredUsers(self, request, context):
        print("Received Request")
        product_id = request.productId
        product_address = request.productAddress
        volunteer_list = request.volunteerList

        product_coord = extra_functions.convertAddress(product_address)
        if product_coord is None:
            return locate_pb2.responseBody(
                productId=product_id,
                productClosestCC=None,
                userList=[],
                error="Not a valid address!"
            )
        
        closest_cc = extra_functions.find_closest_cc(product_coord)
        if closest_cc is None:
            return locate_pb2.responseBody(
                productId=product_id,
                productClosestCC=None,
                userList=[],
                error="Can't find closest CC!"
            )
        
        center_point_coord = extra_functions.get_center_point(product_coord,closest_cc["coordinates"])
        volunteer_list = volunteer_list
        filtered_closest_list = extra_functions.find_closest_users(center_point_coord,volunteer_list)

        reponse = locate_pb2.responseBody(
            productId = product_id,
            productClosestCC = f"{closest_cc['display_name']}|{closest_cc['address']}",
            userList = filtered_closest_list,
            error = None
        )
        return reponse

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    locate_pb2_grpc.add_locateServicer_to_server(LocateService(), server)
    server.add_insecure_port("0.0.0.0:5006")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()