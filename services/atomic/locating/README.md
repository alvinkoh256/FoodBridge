# Locating Service

A gRPC service that helps match volunteers with food donation pickups based on proximity.

## Overview

This service finds the closest community center to a food donation and then identifies volunteers 
who are geographically positioned to efficiently pick up the donation.

## API

### getFilteredUsers

Filters a list of volunteer users based on their proximity to a center point between a product 
location and the nearest community center.

**Request**:
- `productId`: Unique identifier for the product/donation
- `productAddress`: Physical address of the product
- `volunteerList`: List of potential volunteers with their locations

**Response**:
- `productId`: Echo of the product ID
- `productClosestCC`: Information about the closest community center
- `userList`: Filtered list of volunteers sorted by proximity
- `error`: Error message if any occurred

## Environment Variables

- `GRPC_PORT`: (Optional) Port on which the gRPC server listens (default: 5006)

## Building and Running

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python locating.py