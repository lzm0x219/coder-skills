/** 拟议 v2 声明；保留 v1 调用形态。尚未实现或发布。 */
export interface Item {
  readonly id: string;
  readonly title: string;
}

export interface Page<T> {
  readonly items: readonly T[];
  readonly nextCursor?: string;
}

export interface ListOptions {
  /** 保留 v1 含义、默认值与范围；新代码建议使用 pageSize。 */
  readonly limit?: number;
  /** 本次新增的同义参数；默认 50，范围 1..100。 */
  readonly pageSize?: number;
  readonly cursor?: string;
}

export type SearchErrorCode = "invalid_input" | "permission_denied" | "transport_failure";

export declare class SearchError extends Error {
  readonly code: SearchErrorCode;
}

export declare class SearchClient {
  listPage(options?: ListOptions): Promise<Page<Item>>;
}
