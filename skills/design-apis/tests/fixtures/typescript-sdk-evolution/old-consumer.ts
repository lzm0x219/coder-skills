/** 此文件代表已存在的消费者；测试候选版本时保持调用代码不变。 */
import { SearchError, type Item, type SearchClient } from "@example/search";

export async function listTitles(client: SearchClient): Promise<readonly string[]> {
  try {
    const page = await client.listPage({ limit: 25 });
    return page.items.map((item: Item) => item.title);
  } catch (error) {
    if (error instanceof SearchError && error.code === "permission_denied") {
      throw new Error("当前身份无权读取搜索结果", { cause: error });
    }
    throw error;
  }
}
