export interface Item {
    name: string;
    cents: number;
}
export declare function total(items: readonly Item[], discount?: number): number;
export declare function format(cents: number): string;
export declare function receipt(items: readonly Item[], discount?: number): string;
