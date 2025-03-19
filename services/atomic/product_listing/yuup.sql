delimeter $$
    create trigger before_product_insert 
    before insert on product_listing for each row

    BEGIN
        new.product_listing.productId = new uuid()
        new.product_listing.productTimeStamp = new Date()
    END$$

delimeter ;
