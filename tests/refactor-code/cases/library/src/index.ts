export interface Item { name: string; cents: number }
export function total(items: readonly Item[], discount = 0): number {
  if (discount < 0 || discount > 1) throw new RangeError('discount');
  return Math.round(items.reduce((sum, item) => sum + item.cents, 0) * (1 - discount));
}
export function format(cents: number): string { return (cents / 100).toFixed(2); }
export function receipt(items: readonly Item[], discount = 0): string {
  return items.map(item => item.name).join(',') + ':' + format(total(items, discount));
}
