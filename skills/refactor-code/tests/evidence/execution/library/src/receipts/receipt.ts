import { Item, total } from '../billing/amount';
import { format } from '../presentation/money';
export function receipt(items: readonly Item[], discount = 0): string {
  return items.map(item => item.name).join(',') + ':' + format(total(items, discount));
}
