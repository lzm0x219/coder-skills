import { Item, total, format, receipt } from './src';
const items: readonly Item[] = [{name: 'tea', cents: 105}];
const amount: number = total(items, 0.1);
const lines: string[] = [format(amount), receipt(items)];
console.log(lines);
