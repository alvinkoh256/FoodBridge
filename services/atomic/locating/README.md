# Locating Service

A gRPC service that helps match volunteers with food donation pickups based on proximity.

## Overview

This service finds the closest community center to a food donation and then identifies volunteers who are geographically positioned to efficiently pick up the donation.

## Protocol Buffer Definition

```proto
syntax = "proto3";

service locate {
    rpc getFilteredUsers(inputBody) returns (responseBody){};
}

message volunteerInfo {
    string userId = 1;
    string userAddress = 2;
}

message inputBody {
    string productId = 1;
    string productAddress = 2;
    string productHubAddress = 3;
    repeated volunteerInfo volunteerList = 4;
}

message responseBody {
    string productId = 1;
    repeated string userList = 2;
    string productClosestCC = 3;
    string error = 4;
}
```
## Example Input

Below is an example JSON message sent to the `getFilteredUsers` RPC method:

```json
{
  "productId": "123",
  "productAddress": "123 Main St, Singapore",
  "productHubAddress": "456 Hub Ave, Singapore",
  "volunteerList": [
    {
      "userId": "vol1",
      "userAddress": "789 Side St, Singapore"
    },
    {
      "userId": "vol2",
      "userAddress": "321 Far Rd, Singapore"
    }
  ]
}
```
## Example Output

This is an example output returned by the service:

```json
{
  "productId": "123",
  "userList": ["vol1", "vol2"],
  "error": ""
}

