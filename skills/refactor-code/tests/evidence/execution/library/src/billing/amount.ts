export interface Item { name: string; cents: number }
export function total(items: readonly Item[], discount = 0): number {
  if (discount < 0 || discount > 1) throw new RangeError('discount');
  return Math.round(items.reduce((sum, item) => sum + item.cents, 0) * (1 - discount));
}
