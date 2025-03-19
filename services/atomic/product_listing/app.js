import { retrieveAll, createProductListing, updateProduct, deleteProduct, uploadPicture } from './server.js'
import express from 'express'
import multer from 'multer'
import cors from 'cors' // Add this import

const app = express()
const PORT = 5005

// Enable CORS for all routes
app.use(cors({
    origin: '*', // Allow all origins
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}))

app.listen(PORT, (error) =>{
        if(!error){
            console.log("Server is Successfully Running, and App is listening on port "+ PORT)
        }
        else{
            console.log("Error occurred, server can't start", error)
        }
    }
);

app.use(express.json());
app.post('/', (req, res)=>{
    const {name} = req.body
    
    res.send(`Welcome ${name}`)
})

app.get('/products', async (req, res) => {
    try {
        const products = await retrieveAll()
        res.json(products)
    } catch (err) {
        res.status(500).json({ error: err.message })
    }
});

const upload = multer({ storage: multer.memoryStorage() })

app.post('/product', upload.single('productPic'), async (req, res)=>{
    try {
        const imageInput = req.file
        const body = req.body
    
        const createResult = await createProductListing(body)
        console.log(createResult)
        const productId = createResult[0].productId
        const filePath = await uploadPicture(imageInput,productId)
        const updateBody = {
            productId:productId,
            productPic:filePath
        }
        const result = await updateProduct(updateBody)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }

})

app.put('/productCCAndUsers', async (req,res)=>{
    const body = req.body
    try {
        const result = await updateProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

app.put('/productStatus', async (req,res)=>{
    const body = req.body
    try {
        const result = await updateProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

app.delete('/product', async (req,res)=>{
    const body = req.body
    try {
        const result = await deleteProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})