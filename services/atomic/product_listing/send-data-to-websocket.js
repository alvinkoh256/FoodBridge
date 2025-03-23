import axios from "axios"
import { retrieveAllWhenCCAndUserListExist } from "./server.js"

const websocketUrl = process.env.WEBSOCKET_URL || "http://localhost:5014"
console.log(`Using WebSocket URL: ${websocketUrl}`)

async function sendToWebSocket() {
    try {
        console.log("Retrieving products to send to WebSocket...");
        let allProducts = await retrieveAllWhenCCAndUserListExist();
        console.log(`Sending ${allProducts.length} products to WebSocket at ${websocketUrl}`);

        const response = await axios.post(`${websocketUrl}/sendProductListing`, allProducts);
        
        console.log("WebSocket Response:", response.status, response.statusText);
        if (response.data) {
            console.log("Response Data:", response.data);
        }
    } catch (error) {
        console.error("Error sending data to WebSocket:", error.message);
        if (error.response) {
            console.error("Response status:", error.response.status);
            console.error("Response data:", error.response.data);
        } else if (error.request) {
            console.error("No response received from WebSocket service");
        }
    }
}

export { sendToWebSocket }