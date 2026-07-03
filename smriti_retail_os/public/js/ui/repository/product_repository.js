/**
 * @file:    public/js/ui/repository/product_repository.js
 * @desc:    Front-end Repository Layer for SMRITI Product Studio.
 *           Isolates backend API calls from application code.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};
SMRITI.Repository = SMRITI.Repository || {};

SMRITI.Repository.ProductRepository = (function() {
    
    // Core helper to call whitelisted backend python endpoints
    function callAPI(method, args = {}) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: method,
                args: args,
                callback: function(r) {
                    if (r.exc) {
                        reject(new Error(r.exc));
                    } else {
                        resolve(r.message);
                    }
                },
                error: function(err) {
                    reject(err);
                }
            });
        });
    }

    return {
        getProducts: function(limit = 200) {
            return callAPI("smriti_retail_os.item_studio.api.product_api.get_products", { limit: limit });
        },

        getProductDetail: function(itemCode) {
            return callAPI("smriti_retail_os.item_studio.api.product_api.get_product_detail", { item_code: itemCode });
        },

        saveProduct: function(itemData, itemCode = null) {
            return callAPI("smriti_retail_os.item_studio.api.product_api.save_product", {
                item_data: itemData,
                item_code: itemCode
            });
        },

        deleteProduct: function(itemCode) {
            return callAPI("smriti_retail_os.item_studio.api.product_api.delete_product", { item_code: itemCode });
        }
    };
})();
