"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.total = total;
function total(items, discount = 0) {
    if (discount < 0 || discount > 1)
        throw new RangeError('discount');
    return Math.round(items.reduce((sum, item) => sum + item.cents, 0) * (1 - discount));
}
