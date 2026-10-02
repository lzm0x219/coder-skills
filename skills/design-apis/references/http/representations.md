# HTTP 表示、文件传输与缓存

仅在 API 传递媒体/大型对象、部分表示、多个内容格式或可缓存响应时读取。Range 和内容协商是可选能力；未实现时必须按普通请求语义处理，不假装支持。

**H28｜表示元数据｜有 JSON/二进制/多格式表示时。** 为每个成功和错误响应定义 Content-Type、字符编码、内容编码、Content-Length（可未知时说明）与可用协商头；拒绝不支持的请求媒体类型用明确定义的 415，无法生成所选响应格式时定义 406/回退行为。描述 JSON 数字精度、时间、空值和大文件 URI 与字节内容的区别。代理/客户端据 Content-Type 选择解析器，不能让同一 media type 对字段语义漂移。证据：支持/不支持媒体类型、Accept 组合、压缩前后。参考：[RFC 9110 §§8,12](https://www.rfc-editor.org/rfc/rfc9110.html#section-8)。

**H29｜Range 下载｜支持断点续传/随机访问时。** 仅对 GET 表示定义 byte ranges 与 `Accept-Ranges`；成功部分响应使用 206 和匹配表示的 `Content-Range`，不可满足范围按 RFC 的 416 规则。`If-Range` 验证器不匹配时退回完整 200，调用方丢弃旧分块，不能拼接不同 ETag/表示编码的片段。说明多 range 是否支持、并发修改时的验证器及错误恢复；Range 不应改变写方法语义。若不支持，忽略 Range 或用适当错误遵守选择，不能返回伪造的 206。证据：首/尾/超界 range、ETag 命中和失配、对象改变后续传。依据：[RFC 9110 §14](https://www.rfc-editor.org/rfc/rfc9110.html#section-14)。

**H30｜大文件上传/下载｜对象太大或生命周期独立时。** 选择内联 body、分块/可续传会话、或独立对象存储上传下载 URL，并标出何者属于本 API 契约、何者是第三方协议。定义内容长度/配额校验时机、校验和算法及范围、完成/放弃会话、重复分块覆盖规则、并发冲突、过期清理和最终对象可见性。临时签名 URL 应限制对象/方法/过期与重放范围，且不得把它当作永久资源身份；敏感令牌不能进入日志或错误详情。容量、最大大小、分块尺寸和保留时长均须给测量/产品来源，未知则标候选。证据：截断/重复/乱序块、哈希不匹配、过期链接、完成响应丢失。参考：Azure [API design: large binary resources](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design#implement-large-binary-resources)、[RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html)。

**H31｜缓存范围｜任何响应可被客户端/代理缓存时。** 按响应是否含用户/租户数据选择 `private`、`no-store` 或可共享缓存策略；定义 max-age/s-maxage、Vary 维度、验证器和授权缓存键。若请求带 `Authorization`，shared cache 只有在响应含 RFC 9111 §3.5 允许的明确 Cache-Control 指令时才可复用；`Vary` 不会单独覆盖此禁令。认证头或 Cookie 变化若改变表示，必须隔离缓存键或禁止共享缓存。不能把 no-cache（需验证）误写为 no-store（禁止存储）。证据：匿名/两个身份、不同 Accept/语言、验证器命中以及权限撤销后的缓存行为。依据：[RFC 9111 §§3–5](https://www.rfc-editor.org/rfc/rfc9111.html)。

**H32｜条件和并发｜资源更新可能丢失其他调用方写入时。** 给表示生成与资源版本一一对应的 ETag；对要求乐观并发控制的更新强制 If-Match，缺失和陈旧版本有不同、可识别结果；成功后返回新 validator。检查顺序遵 RFC 9110：先做正常请求检查，再评估 preconditions；若可证明相同变更已成功，可按 RFC 例外确认成功。弱 ETag 不用于 If-Match 强比较。证据：并发读写、缺条件、陈旧/弱 ETag、成功后重复提交。依据：[RFC 9110 §§13.1–13.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1)。
