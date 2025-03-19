import { retrieveAll, createProductListing, updateProduct, deleteProduct, uploadPicture } from './server.js'
import express from 'express'
import multer from 'multer'
import cors from 'cors'
import { swaggerUi, specs } from './swagger.js'

const app = express()
const PORT = 5005

// Enable CORS for all routes
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}))

// Swagger UI setup
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

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

/**
 * @swagger
 * /products:
 *   get:
 *     summary: Get all products
 *     description: Retrieve a list of all product listings
 *     responses:
 *       200:
 *         description: A list of products
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   productId:
 *                     type: string
 *                     example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *                   productAddress:
 *                     type: string
 *                     example: "123 Sunshine Plaza, Singapore 30495893"
 *                   productStatus:
 *                     type: string
 *                     enum: [open, assigned, picked, delivered]
 *                     example: "open"
 *                   productPic:
 *                     type: string
 *                     format: uri
 *                     example: "https://your-storage-url.com/product-image.jpg"
 */
app.get('/products', async (req, res) => {
    try {
        const products = await retrieveAll()
        res.json(products)
    } catch (err) {
        res.status(500).json({ error: err.message })
    }
});

const upload = multer({ storage: multer.memoryStorage() })

/**
 * @swagger
 * /product:
 *   post:
 *     summary: Create a new product listing
 *     description: Upload a product image and specify its address.
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               productPic:
 *                 type: string
 *                 format: binary
 *                 description: The product image file
 *               productAddress:
 *                 type: string
 *                 example: "123 Sunshine Plaza, Singapore 30495893"
 *     responses:
 *       200:
 *         description: Product successfully created
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 productId:
 *                   type: string
 *                   example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productTimeStamp:
 *                   type: string
 *                   format: date-time
 *                   example: "2025-03-19T16:06:13.121895+00:00"
 *                 productPic:
 *                   type: string
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "open"
 *                 productClosestCC:
 *                   type: string
 *                   nullable: true
 *                   example: null
 *                 productUserList:
 *                   type: array
 *                   nullable: true
 *                   items:
 *                     type: string
 *                   example: null
 */
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

/**
 * @swagger
 * /productCCAndUsers:
 *   put:
 *     summary: Update product community center and users
 *     description: Updates the community center and users assigned to a product listing.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               productId:
 *                 type: string
 *                 example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *               productClosestCC:
 *                 type: string
 *                 example: "ABC Community Centre"
 *               productUserList:
 *                 type: array
 *                 items:
 *                   type: string
 *                 example:
 *                   - "1111-1111-1111"
 *                   - "2222-2222-2222"
 *                   - "3333-3333-3333"
 *     responses:
 *       200:
 *         description: Product updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 productId:
 *                   type: string
 *                   example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productTimeStamp:
 *                   type: string
 *                   format: date-time
 *                   example: "2025-03-19T16:06:13.121895+00:00"
 *                 productPic:
 *                   type: string
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "open"
 *                 productClosestCC:
 *                   type: string
 *                   example: "ABC Community Centre"
 *                 productUserList:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example:
 *                     - "1111-1111-1111"
 *                     - "2222-2222-2222"
 *                     - "3333-3333-3333"
 */
app.put('/productCCAndUsers', async (req,res)=>{
    const body = req.body
    try {
        const result = await updateProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

/**
 * @swagger
 * /productStatus:
 *   put:
 *     summary: Update product status
 *     description: Updates the status of a product listing.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               productId:
 *                 type: string
 *                 example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *               productStatus:
 *                 type: string
 *                 enum: [open, assigned, picked, delivered, on-going]
 *                 example: "on-going"
 *     responses:
 *       200:
 *         description: Product status updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 productId:
 *                   type: string
 *                   example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productTimeStamp:
 *                   type: string
 *                   format: date-time
 *                   example: "2025-03-19T16:06:13.121895+00:00"
 *                 productPic:
 *                   type: string
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "on-going"
 *                 productClosestCC:
 *                   type: string
 *                   example: "ABC Community Centre"
 *                 productUserList:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example:
 *                     - "1111-1111-1111"
 *                     - "2222-2222-2222"
 *                     - "3333-3333-3333"
 */
app.put('/productStatus', async (req,res)=>{
    const body = req.body
    try {
        const result = await updateProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

/**
 * @swagger
 * /product:
 *   delete:
 *     summary: Delete a product
 *     description: Deletes a product listing by ID and returns the deleted product details.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               productId:
 *                 type: string
 *                 example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *     responses:
 *       200:
 *         description: Product deleted successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 productId:
 *                   type: string
 *                   example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productTimeStamp:
 *                   type: string
 *                   format: date-time
 *                   example: "2025-03-19T16:06:13.121895+00:00"
 *                 productPic:
 *                   type: string
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "on-going"
 *                 productClosestCC:
 *                   type: string
 *                   example: "ABC Community Centre"
 *                 productUserList:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example:
 *                     - "1111-1111-1111"
 *                     - "2222-2222-2222"
 *                     - "3333-3333-3333"
 */
app.delete('/product', async (req,res)=>{
    const body = req.body
    try {
        const result = await deleteProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})