# Confirm Delivery Service Documentation

## Overview
This service handles confirmation of item drop-offs by volunteers at hub locations. It processes delivery confirmations, notifies volunteers of successful deliveries, and updates the hub inventory.

## Endpoints

### POST /confirmDelivery/drop-off

Confirms a delivery drop-off at a hub location.

#### Request Body

```json
{
  "hubID": 7,
  "volunteerID": 12345,
  "dropOffTime": "2025-03-23T15:30:00",
  "items": [
    {
      "itemName": "Narcissus Mushrooms",
      "quantity": 19
    },
    {
      "itemName": "Sunlight Curry Chicken",
      "quantity": 6
    }
  ],
  "newitems": [
    {
      "itemName": "Tomato Sardines",
      "itemWeight_kg": 0.5,
      "quantity": 10,
      "description": "Canned tomato sardines"
    }
  ]
}
```

#### Request Parameters

| Field | Type | Description |
|-------|------|-------------|
| `hubID` | Integer | ID of the hub where items are dropped off |
| `volunteerID` | Integer | ID of the volunteer making the delivery |
| `dropOffTime` | ISO 8601 DateTime | Time when the drop-off occurred |
| `items` | Array | List of existing items being delivered |
| `newitems` | Array | List of new items being added to inventory |

#### Item Object

| Field | Type | Description |
|-------|------|-------------|
| `itemName` | String | Name of the item |
| `quantity` | Integer | Number of units delivered |

#### New Item Object

| Field | Type | Description |
|-------|------|-------------|
| `itemName` | String | Name of the new item |
| `itemWeight_kg` | Float | Weight of the item in kilograms |
| `quantity` | Integer | Number of units delivered |
| `description` | String | Description of the new item |

## Service Functionality

The service performs the following operations:
1. Retrieves volunteer information from the Account Info service
2. Sends an AMQP message to the Notification service to inform the volunteer of successful drop-off
3. Calls `/hub/updateInventory` to update the hub's inventory with the delivered items

## Dependencies

- Account Info Service
- Notification Service (via AMQP)
- Hub Service