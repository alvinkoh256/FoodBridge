import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

const supaUrl = process.env.SUPABASE_PRODUCT_URL
const supaKey = process.env.SUPABASE_PRODUCT_KEY

const supabase = createClient(supaUrl, supaKey)



async function retrieveAll(){
    const { data, error } = await supabase
        .from('product_listing')
        .select()
    
    if (error) {
        throw new Error(`Failed to retrieve products: ${error.message}`)
    }
    
    return data
}

async function createProductListing(body){
    // let productPic = body.productPic
    let productAddress = body.productAddress
    let productStatus = "open"
    // console.log(`${productPic},${productAddress},${productStatus}`)
    const{data,error} = await supabase.from("product_listing").insert({
        // productPic:productPic,
        productAddress:productAddress,
        productStatus:productStatus
    })
    .select()
    if (error){
        console.log(error.message)
        throw new Error(`Failed to create products: ${error.message}`)
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


export {retrieveAll,createProductListing,updateProduct,deleteProduct,uploadPicture}

