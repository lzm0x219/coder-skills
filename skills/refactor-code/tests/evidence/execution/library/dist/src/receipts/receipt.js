"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.receipt = receipt;
const amount_1 = require("../billing/amount");
const money_1 = require("../presentation/money");
function receipt(items, discount = 0) {
    return items.map(item => item.name).join(',') + ':' + (0, money_1.format)((0, amount_1.total)(items, discount));
}
