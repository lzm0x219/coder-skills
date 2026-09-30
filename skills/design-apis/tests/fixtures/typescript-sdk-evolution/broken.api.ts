/** 负对照：删除已发布的 limit；旧消费者应无法通过类型检查。 */
import type { Item, Page } from "./candidate.api.js";
export type { Item, Page } from "./candidate.api.js";
export { SearchError } from "./candidate.api.js";

export interface ListOptions {
  readonly pageSize?: number;
  readonly cursor?: string;
}

export declare class SearchClient {
  listPage(options?: ListOptions): Promise<Page<Item>>;
}
