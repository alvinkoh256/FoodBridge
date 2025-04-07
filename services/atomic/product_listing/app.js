import { retrieveAllWhenUserListExist, createProductListing, updateProduct, deleteProduct, uploadPicture, getCCByProductId } from './server.js'
import { sendToWebSocket } from './send-data-to-websocket.js'
import express from 'express'
import multer from 'multer'
import cors from 'cors'

import { swaggerUi, specs } from './swagger.js'

const app = express()
app.use(express.json())
app.use(cors({ origin: '*' }))
const PORT = process.env.PORT || 5005

// Swagger UI setup
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

app.listen(PORT,"0.0.0.0", (error) =>{
        if(!error){
            console.log(`Server is Successfully Running, and App is listening on port ${PORT}`)
        }
        else{
            console.log("Error occurred, server can't start", error)
        }
    }
);

/**
 * @swagger
 * /products:
 *   get:
 *     summary: Get all products
 *     description: Retrieve a list of all product listings with volunteer assignments
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
 *                   productTimeStamp:
 *                     type: string
 *                     format: date-time
 *                     example: "2025-03-19T16:06:13.121895+00:00"
 *                   productPic:
 *                     type: string
 *                     format: uri
 *                     example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                   productAddress:
 *                     type: string
 *                     example: "123 Sunshine Plaza, Singapore 30495893"
 *                   productStatus:
 *                     type: string
 *                     enum: [open, assigned, picked, delivered]
 *                     example: "open"
 *                   productCCDetails:
 *                     type: object
 *                     example: {
 *                       "hubId": 1,
 *                       "hubName": "Bedok Orchard RC",
 *                       "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
 *                     }
 *                   productUserList:
 *                     type: array
 *                     items:
 *                       type: string
 *                     example: ["1111-1111-1111", "2222-2222-2222"]
 *                   productItemList:
 *                     type: array
 *                     items:
 *                       type: object
 *                       properties:
 *                         itemName:
 *                           type: string
 *                         quantity:
 *                           type: integer
 *                     example: [
 *                       {"itemName": "tuna", "quantity": 10},
 *                       {"itemName": "beans", "quantity": 10},
 *                       {"itemName": "pickled vegetables", "quantity": 10}
 *                     ]
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Internal server error"
 */
app.get('/products', async (req, res) => {
    try {
        const products = await retrieveAllWhenUserListExist()
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
 *     description: Upload a product image and specify its address, community center details, and item list.
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
 *               productCCDetails:
 *                 type: string
 *                 description: JSON string containing community center details
 *                 example: '{"hubId": 1, "hubName": "Bedok Orchard RC", "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"}'
 *               productItemList:
 *                 type: string
 *                 description: JSON string containing list of food items
 *                 example: '[{"itemName":"tuna","quantity":10},{"itemName":"beans","quantity":10},{"itemName":"pickled vegetables","quantity":10}]'
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
 *                 productCCDetails:
 *                   type: object
 *                   example: {
 *                     "hubId": 1,
 *                     "hubName": "Bedok Orchard RC",
 *                     "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
 *                   }
 *                 productUserList:
 *                   type: array
 *                   nullable: true
 *                   items:
 *                     type: string
 *                   example: null
 *                 productItemList:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       itemName:
 *                         type: string
 *                       quantity:
 *                         type: integer
 *                   example: [
 *                     {"itemName": "tuna", "quantity": 10},
 *                     {"itemName": "beans", "quantity": 10},
 *                     {"itemName": "pickled vegetables", "quantity": 10}
 *                   ]
 *       400:
 *         description: Bad request - missing required fields
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Missing required field"
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Internal server error"
 */
app.post('/product', upload.single('productPic'), async (req, res)=>{
    try {
        const imageInput = req.file;
        const body = req.body;
        
        if (!imageInput) {
            return res.status(400).json({ 
                error: "Missing product image file. Please upload a file with field name 'productPic'." 
            });
        }
        
        if (!body.productAddress) {
            return res.status(400).json({ 
                error: "Missing productAddress field" 
            });
        }
        
        
        if (!body.productItemList) {
            return res.status(400).json({ 
                error: "Missing productItemList field" 
            });
        }
        
        const createResult = await createProductListing(body);
        const productId = createResult[0].productId;
        
        const filePath = await uploadPicture(imageInput, productId);
        
        const updateBody = {
            productId: productId,
            productPic: filePath
        };
        
        const result = await updateProduct(updateBody);
        await sendToWebSocket() 
        res.status(200).json(result[0]);
    } catch (error) {
        console.error("Error in /product endpoint:", error);
        res.status(500).json({ error: error.message });
    }
})

/**
 * @swagger
 * /product:
 *   put:
 *     summary: Update a product listing
 *     description: Update product details such as status, user list, or community center details
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - productId
 *             properties:
 *               productId:
 *                 type: string
 *                 example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *               productStatus:
 *                 type: string
 *                 enum: [open, assigned, picked, delivered]
 *                 example: "assigned"
 *               productUserList:
 *                 type: array
 *                 items:
 *                   type: string
 *                 example: ["1111-1111-1111", "2222-2222-2222"]
 *               productCCDetails:
 *                 type: object
 *                 example: {
 *                   "hubId": 1,
 *                   "hubName": "Bedok Orchard RC",
 *                   "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
 *                 }
 *               productPic:
 *                 type: string
 *                 format: uri
 *                 example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *     responses:
 *       200:
 *         description: Product successfully updated
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
 *                   format: uri
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "assigned"
 *                 productCCDetails:
 *                   type: object
 *                   example: {
 *                     "hubId": 1,
 *                     "hubName": "Bedok Orchard RC",
 *                     "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
 *                   }
 *                 productUserList:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example: ["1111-1111-1111", "2222-2222-2222"]
 *                 productItemList:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       itemName:
 *                         type: string
 *                       quantity:
 *                         type: integer
 *                   example: [
 *                     {"itemName": "tuna", "quantity": 10},
 *                     {"itemName": "beans", "quantity": 10},
 *                     {"itemName": "pickled vegetables", "quantity": 10}
 *                   ]
 *       400:
 *         description: Bad request - missing productId or invalid data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Missing productId field"
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Internal server error"
 */
app.put('/product', async (req,res)=>{
    const body = req.body
    try {
        const result = await updateProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
    await sendToWebSocket()
})


app.get('/productCC/:productId',async(req,res)=>{
    const productId = req.params["productId"]
    try {
        const result = await getCCByProductId(productId)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

/**
 * @swagger
 * /product:
 *   delete:
 *     summary: Delete a product listing
 *     description: Deletes a product listing by ID and sends a WebSocket update notification
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - productId
 *             properties:
 *               productId:
 *                 type: string
 *                 example: "190038b4-2911-4e43-956d-9f31cb55a869"
 *     responses:
 *       200:
 *         description: Product successfully deleted
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
 *                   format: uri
 *                   example: "https://vdiqdxayroxnapzbyhzi.supabase.co/storage/v1/object/public/esd-products/products/190038b4-2911-4e43-956d-9f31cb55a869"
 *                 productAddress:
 *                   type: string
 *                   example: "123 Sunshine Plaza, Singapore 30495893"
 *                 productStatus:
 *                   type: string
 *                   example: "open"
 *                 productCCDetails:
 *                   type: object
 *                   example: {
 *                     "hubId": 1,
 *                     "hubName": "Bedok Orchard RC",
 *                     "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
 *                   }
 *                 productUserList:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example: ["1111-1111-1111", "2222-2222-2222"]
 *       400:
 *         description: Bad request - missing productId
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Missing productId field"
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Internal server error"
 */
app.delete('/product', async (req,res)=>{
    const body = req.body
    try {
        const result = await deleteProduct(body)
        res.status(200).json(result[0])
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
    await sendToWebSocket()
})
