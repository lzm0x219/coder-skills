"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const src_1 = require("./src");
const items = [{ name: 'tea', cents: 105 }];
const amount = (0, src_1.total)(items, 0.1);
const lines = [(0, src_1.format)(amount), (0, src_1.receipt)(items)];
console.log(lines);
