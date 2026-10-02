/** 新消费者使用明确的一页大小参数。 */
import { type SearchClient } from "@example/search";

export async function firstPage(client: SearchClient) {
  const page = await client.listPage({ pageSize: 25 });
  return { items: page.items, nextCursor: page.nextCursor };
}
