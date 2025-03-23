import express from 'express'
import { createServer } from "http"
import { Server } from "socket.io"
import path from "path";

const app = express()
app.use(express.json()) //Places the express middleware that parses json req

// creates http server that uses the express app to handle http requests
const httpServer = createServer(app)
const io = new Server(httpServer,{
    cors:{
        origin: "*"
    }
})

io.on("connection",(socket)=>{
    console.log(`User: ${socket.id} connected`)

    socket.on("disconnect", () => {
        console.log("A user disconnected")
    })

})

app.post('/sendProductListing',async (req,res)=>{
    try {
        let result = req.body
        io.emit('productListingRoom', result)
        res.status(200).json("SUCCESS")
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

const PORT = 5014
httpServer.listen(PORT, ()=>console.log(`Listening on port ${PORT}`))