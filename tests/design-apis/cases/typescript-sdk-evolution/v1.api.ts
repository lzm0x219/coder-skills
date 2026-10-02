/** 已发布 v1 的演练契约；仅供兼容性设计测试。 */
export interface Item {
  readonly id: string;
  readonly title: string;
}

export interface Page<T> {
  readonly items: readonly T[];
  readonly nextCursor?: string;
}

export interface ListOptions {
  /** 默认 50，范围 1..100；仅取一页。 */
  readonly limit?: number;
  readonly cursor?: string;
}

export type SearchErrorCode = "invalid_input" | "permission_denied" | "transport_failure";

export declare class SearchError extends Error {
  readonly code: SearchErrorCode;
}

export declare class SearchClient {
  listPage(options?: ListOptions): Promise<Page<Item>>;
}
