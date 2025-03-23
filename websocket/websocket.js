import express from 'express'
import { createServer } from "http"
import { Server } from "socket.io"
import cors from 'cors'


const app = express()
app.use(express.json()) //Places the express middleware that parses json req

// Enable CORS for all routes
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}))

// creates http server that uses the express app to handle http requests
const httpServer = createServer(app)
const io = new Server(httpServer,{
    cors:{
        origin: "*"
    }
})

io.on("connection", (socket) => {
    console.log(`User: ${socket.id} connected`)
    console.log(`Total connected clients: ${io.engine.clientsCount}`)

    socket.on("disconnect", () => {
        console.log(`User: ${socket.id} disconnected`)
        console.log(`Total connected clients: ${io.engine.clientsCount}`)
    })

    socket.emit('message', { 
        message: 'Connected to FoodBridge WebSocket Server',
        socketId: socket.id 
    })
})

app.post('/sendProductListing',async (req,res)=>{
    try {
        let result = req.body
        console.log(`Received product listing update with ${Array.isArray(result) ? result.length : 0} products`)
        
        io.emit('productListingRoom', result)
        // Log the response details
        const response = { 
            status: "SUCCESS",
            message: "Product listing broadcast to all connected clients",
            clientCount: io.engine.clientsCount
        }
        console.log("Sending response:", response)
        res.status(200).json(response)
    } catch (error) {
        console.error("Error broadcasting product listing:", error.message)
        res.status(500).json({ error: error.message })
    }
})

// Health check endpoint
app.get('/health', (req, res) => {
    const status = {
        status: 'healthy',
        clientCount: io.engine.clientsCount
    }
    console.log("Health check requested, responding:", status)
    res.status(200).json(status)
})

const PORT = 5014
httpServer.listen(PORT, '0.0.0.0', () => {
    console.log(`WebSocket server listening on port ${PORT}`)
    console.log(`Health check available at http://localhost:${PORT}/health`)
})