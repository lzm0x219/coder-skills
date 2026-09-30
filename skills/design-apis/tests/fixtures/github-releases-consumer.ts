/** 真实 GitHub REST API 的最小消费者；用于检查 SDK 命名与分页设计，不是 SDK 实现。 */
export async function fetchReleasePage(owner: string, repo: string, page = 1, pageSize = 2) {
  if (!owner || !repo || !Number.isInteger(page) || page < 1 || !Number.isInteger(pageSize) || pageSize < 1 || pageSize > 100) {
    throw new Error("invalid_input");
  }

  const url = new URL(`https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases`);
  url.searchParams.set("page", String(page));
  url.searchParams.set("per_page", String(pageSize));

  const response = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2026-03-10",
      "User-Agent": "coder-skills-design-review",
    },
  });
  if (!response.ok) throw new Error(`GitHub HTTP ${response.status}`);

  const data: unknown = await response.json();
  if (!Array.isArray(data) || !data.every((item) => typeof item === "object" && item !== null && typeof item.id === "number" && typeof item.tag_name === "string")) {
    throw new Error("unexpected_response");
  }

  return {
    items: data.map((item) => ({ id: item.id as number, tagName: item.tag_name as string })),
    hasNext: /rel="next"/.test(response.headers.get("link") ?? ""),
  };
}
