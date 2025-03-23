import axios from "axios"
import { retrieveAllWhenCCAndUserListExist } from "./server.js"

const websocketUrl = "http://localhost:5014"

async function sendToWebSocket() {
    try {
        let allProducts = await retrieveAllWhenCCAndUserListExist();

        const response = await axios.post(`${websocketUrl}/sendProductListing`, allProducts);
        
        console.log("Response Data:", response.data);

        if (response.data?.response?.parameters) {
            console.log("Result:", response.data.response.parameters);
        }

    } catch (error) {
        console.error("Error sending data:", error.message);
    }
}

export { sendToWebSocket }