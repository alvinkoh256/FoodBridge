from concurrent import futures
import grpc
import locate_pb2
import locate_pb2_grpc
import os
import logging

import extra_functions

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocateService(locate_pb2_grpc.locateServicer):
    def getFilteredUsers(self, request, context):
        logger.info("Received Request")
        
        # Extract request data
        product_id = request.productId
        product_address = request.productAddress
        product_hub_address = request.productHubAddress
        volunteer_list = request.volunteerList
        
        # Validate product address
        try:
            product_coord = extra_functions.convertAddress(product_address)
            if product_coord is None:
                return locate_pb2.responseBody(
                    productId=product_id,
                    userList=[],
                    error="Not a valid product address!"
                )
        except Exception as e:
            logger.error(f"Error converting product address: {str(e)}")
            return locate_pb2.responseBody(
                productId=product_id,
                userList=[],
                error=f"Product address conversion error: {str(e)}"
            )
        
        # Convert hub address to coordinates
        try:
            hub_coord = extra_functions.convertAddress(product_hub_address)
            if hub_coord is None:
                return locate_pb2.responseBody(
                    productId=product_id,
                    userList=[],
                    error="Not a valid hub address!"
                )
        except Exception as e:
            logger.error(f"Error converting hub address: {str(e)}")
            return locate_pb2.responseBody(
                productId=product_id,
                userList=[],
                error=f"Hub address conversion error: {str(e)}"
            )
        
        # Calculate center point and find closest users
        try:
            center_point_coord = extra_functions.get_center_point(product_coord, hub_coord)
            filtered_closest_list = extra_functions.find_closest_users(center_point_coord, volunteer_list)
        except Exception as e:
            logger.error(f"Error in filtering users: {str(e)}")
            return locate_pb2.responseBody(
                productId=product_id,
                userList=[],
                error=f"User filtering error: {str(e)}"
            )

        # Create and return response
        try:
            response = locate_pb2.responseBody(
                productId=product_id,
                userList=filtered_closest_list,
                error=None
            )
            return response
        except Exception as e:
            logger.error(f"Error creating response: {str(e)}")
            return locate_pb2.responseBody(
                productId=product_id,
                userList=[],
                error=f"Response creation error: {str(e)}"
            )
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    locate_pb2_grpc.add_locateServicer_to_server(LocateService(), server)
    port = os.getenv('GRPC_PORT', '5006')
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()