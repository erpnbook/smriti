/**
 * @file:    public/js/ui/service/product_service.js
 * @desc:    Front-end Application Service Layer for SMRITI Product Studio.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};
SMRITI.Service = SMRITI.Service || {};

SMRITI.Service.ProductService = (function() {
    const repo = SMRITI.Repository.ProductRepository;

    return {
        getProducts: async function(limit = 200) {
            return await repo.getProducts(limit);
        },

        getProductDetail: async function(itemCode) {
            return await repo.getProductDetail(itemCode);
        },

        saveProduct: async function(itemData, itemCode = null) {
            // Validate client-side bounds
            if (!itemData.item_name) {
                throw new Error("Product Description is required.");
            }
            if (parseFloat(itemData.cost_price || 0) > parseFloat(itemData.mrp || 0)) {
                throw new Error("Cost Price cannot exceed MRP.");
            }
            
            return await repo.saveProduct(itemData, itemCode);
        },

        deleteProduct: async function(itemCode) {
            return await repo.deleteProduct(itemCode);
        },

        bulkDeleteProducts: async function(itemCodes) {
            if (!itemCodes || !itemCodes.length) throw new Error("No items selected for deletion.");
            return await repo.bulkDeleteProducts(itemCodes);
        }
    };
})();
