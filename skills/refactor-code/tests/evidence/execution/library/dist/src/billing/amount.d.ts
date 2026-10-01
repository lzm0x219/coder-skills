export interface Item {
    name: string;
    cents: number;
}
export declare function total(items: readonly Item[], discount?: number): number;
