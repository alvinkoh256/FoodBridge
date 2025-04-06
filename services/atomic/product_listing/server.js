import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

const supaUrl = process.env.SUPABASE_PRODUCT_URL
const supaKey = process.env.SUPABASE_PRODUCT_KEY

console.log(`Supabase URL configured: ${!!supaUrl}`)
console.log(`Supabase Key configured: ${!!supaKey}`)

if (!supaUrl || !supaKey) {
  console.error('Missing required Supabase environment variables')
}

const supabase = createClient(supaUrl, supaKey)


async function retrieveAllWhenUserListExist(){
    const { data, error } = await supabase
        .from('product_listing')
        .select()
        .not('productUserList','is',null)
    
    if (error) {
        throw new Error(`Failed to retrieve products: ${error.message}`)
    }
    
    return data
}

async function getCCByProductId(productId){
    const { data, error } = await supabase
    .from('product_listing')
    .select('productCCDetails')
    .eq('productId',productId)

    if (error) {
        throw new Error(`Failed to retrieve products: ${error.message}`)
    }

    return data
}

async function createProductListing(body){
    let productAddress = body.productAddress
    let productItemList = body.productItemList
    let userId = body.productUserId

    
    // Log the incoming data to see what's happening
    console.log("Type:", typeof productCCDetails);

    // Fix the parsing - use the local variable, not body.productCCDetails
    if(typeof productItemList === "string"){
        try {
            productItemList = JSON.parse(productItemList)
        } catch (err) {
            console.error("Error parsing productItemList:", err);
        }
    }
    
    let productStatus = "open"
    const{data,error} = await supabase.from("product_listing").insert({
        productAddress:productAddress,
        productStatus:productStatus,
        productItemList:productItemList,
        productUserId:userId
    })
    .select()
    if (error){
        console.log(error.message)
        throw new Error(`Failed to create products: ${error.message}`)
    }
    return data
}

async function getProductByUserId(userId){
    const { data, error } = await supabase
    .from('product_listing')
    .select('*')
    .eq('productUserId',userId)

    if (error) {
        throw new Error(`Failed to retrieve products: ${error.message}`)
    }

    return data
}

async function updateProduct(body){
    const { data,error } = await supabase
        .from('product_listing')
        .update(
            body
        )
        .eq('productId', body.productId)
        .select()
    if (error){
        throw new Error(`Failed to update product: ${error.message}`)
    }
    return data
}


async function deleteProduct(body){
    let productId = body.productId
    const { data, error } = await supabase
        .from('product_listing')
        .delete()
        .eq('productId', productId)
        .select()
    if (error){
        throw new Error(`Failed to delete product: ${error.message}`)
    }
    return data
}

// function to store file in blob with file as input
async function uploadPicture(image,productId){
    const fileType = image.mimetype
    const { data, error } = await supabase
        .storage
        .from('esd-products')
        .upload(`products/${productId}`, image.buffer, {
            contentType: fileType,
            cacheControl: '3600',
            upsert: false
        })
    if (error){
        throw new Error(`Failed to delete product: ${error.message}`)
    }
    const returnFilePath = `${supaUrl}/storage/v1/object/public/${data.fullPath}`
    return returnFilePath
}


export {retrieveAllWhenUserListExist,createProductListing,updateProduct,deleteProduct,uploadPicture,getCCByProductId, getProductByUserId}

