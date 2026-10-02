# HTTP 浏览器跨源策略

只在 browser JavaScript 从与 API 不同的 origin 发请求时读取。CORS 是浏览器的读取/预检策略，不是身份认证或资源授权。

**H39｜CORS 来源范围｜浏览器跨 origin 调用时。** 列出允许的 origin、method、request header、exposed response header 和 credentials 行为；动态回显 Origin 时按规范返回 `Vary: Origin`。携带 credentials 时不能使用 `Access-Control-Allow-Origin: *`，应返回经验证的精确 allowlist origin；不能把任意 `Origin` 反射当作授权。预检 response 必须覆盖实际使用的 method/headers，Range、Authorization、ETag 等需列入对应策略；浏览器读取恢复所需 header 也需 expose。改变 allowlist/凭据策略须纳入 cache 变体和 CSRF threat model。证据：允许/拒绝 origin、简单请求、带 Authorization/Range 的预检、credentialed request、跨缓存 origin。依据：[WHATWG Fetch CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)、OWASP [HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)。通用身份/权限/CSRF 评估见[共享安全契约](../common/security.md)CS06。
