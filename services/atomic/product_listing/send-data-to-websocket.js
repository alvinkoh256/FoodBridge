import { axios } from "axios"
import { retrieveAll } from "./server"
import { response } from "express"


// set url port

// function to do axios post with url
    // run the retrieveall 
    // try
        // get the data and send it
    // catch
        // yuup

const websocketUrl = "http://localhost:5006"

async function sendToWebsocket() {
    try {
        let allProducts = await retrieveAll();

        const response = await axios.post(`${websocketUrl}/sendData`, allProducts);
        
        console.log("Response Data:", response.data);

        if (response.data?.response?.parameters) {
            console.log("Result:", response.data.response.parameters);
        }

    } catch (error) {
        console.error("Error sending data:", error.message);
    }
}

export { sendToWebsocket }