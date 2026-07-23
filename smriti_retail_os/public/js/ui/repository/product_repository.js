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
                    if (r && r.exc) {
                        // Extract readable message from server exception
                        let msg = r.exc;
                        try {
                            const parsed = JSON.parse(r.exc);
                            if (Array.isArray(parsed)) msg = parsed[parsed.length - 1];
                        } catch (e) { /* keep raw */ }
                        reject(new Error(String(msg).split('\n').pop() || 'Server error'));
                    } else {
                        resolve(r ? r.message : null);
                    }
                },
                error: function(xhr) {
                    let msg = 'Request failed';
                    try {
                        const body = JSON.parse(xhr.responseText);
                        msg = body.exception || body.message || msg;
                    } catch (e) { /* keep default */ }
                    reject(new Error(msg));
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
        },

        bulkDeleteProducts: function(itemCodes) {
            // Frappe serialises JS arrays as JSON strings — pass as JSON string explicitly
            return callAPI("smriti_retail_os.item_studio.api.product_api.bulk_delete_products", {
                item_codes: JSON.stringify(itemCodes)
            });
        }
    };
})();
