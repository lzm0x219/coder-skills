# WebSocket

仅在采用 RFC 6455 WebSocket 时使用；若使用 HTTP/2 extended CONNECT，还需检查 [RFC 8441](https://www.rfc-editor.org/rfc/rfc8441)。RFC 定义 handshake、frame、message、close 和 Origin 安全模型，不定义应用消息 envelope、ACK、持久订阅或业务 cursor。并用[实时总则](../realtime.md)。

**WS01｜Handshake｜规范 MUST + Skill MUST。** 按实际 HTTP 绑定分别核验：HTTP/1.1 Upgrade 按 RFC6455 §4 检查握手字段、版本及 Key/Accept 计算；HTTP/2 extended CONNECT 按 RFC8441 §§3–5 检查 `SETTINGS_ENABLE_CONNECT_PROTOCOL`、CONNECT 与 `:protocol = websocket`，不处理 Sec-WebSocket-Key/Accept，不能套用 HTTP/1.1 的 Connection/Upgrade 与 101。明确 endpoint、TLS (wss)、认证位置、失败状态和 subprotocol。若选择 subprotocol，服务端只能选择客户端提供的一个；规范也允许不选择。若应用必须协商 envelope/版本，Skill MUST 声明未协商时拒绝；若允许无 subprotocol，声明其应用合同，不能从沉默推断双方采用同一版本。依据：[RFC6455 §4/§1.9](https://www.rfc-editor.org/rfc/rfc6455#section-4)、[RFC8441 §§3–5](https://www.rfc-editor.org/rfc/rfc8441#section-3)。

**WS02｜Origin 与身份｜规范 SHOULD + Skill MUST。** 面向浏览器页面且只接受可信站点的服务按 RFC6455 §10.2 allowlist 验证 Origin，拒绝时 handshake 返回 403；同时单独验证身份/授权。非浏览器客户端可任意伪造 Origin，因此它不是认证。cookie 认证需有 CSWSH/CSRF 边界；URL token 会进入日志/历史时避免采用。依据：[RFC6455 §10.2/§10.5](https://www.rfc-editor.org/rfc/rfc6455#section-10.2)。

**WS03｜Frames 与 messages｜规范 MUST。** 应用以完整 message 为解析单位，不暴露未完成 fragment；同一 message fragments 有序、不得交错，Control frame 不分片且允许插入分片序列之间。Text payload 是 UTF-8；binary payload 格式由应用协议明确。协议不能把 frame 边界当一条业务消息边界。依据：RFC6455 §5、§6。

**WS04｜Control/close｜规范 MUST + Skill MUST。** 明确 Ping/Pong 仅作 transport control，不能冒充业务 ACK。close 使用 closing handshake；关闭码和 reason 用 RFC/IANA 允许的范围，不发送保留码或超长/非法 UTF-8 reason。契约列正常 close、服务重启、认证过期、速率/大小超限、协议错误各自 close code 与客户端动作；异常关闭后的自动重连不应用于永久策略错误。依据：RFC6455 §5.5、§7.1–7.4。

**WS05｜Reconnect｜规范 SHOULD + Skill MUST。** 异常关闭后客户端使用随机首轮等待与逐次增长退避（例如截断指数退避）；规则不给业务固定统一秒数。加入总重连预算/jitter 与认证/协议错误停止条件，恢复时重建 subscription 并携带业务 cursor，去重重复 event。正常 close 是否重连由业务策略决定。依据：RFC6455 §7.2.3。

**WS06｜Limits｜规范 MUST + Skill MUST。** RFC 要求实现对自身 frame size 或重组后的总 message size 限制采取保护措施；服务契约分别给 inbound/outbound frame/message 字节限制、队列/backpressure、超限后 close/error、客户端恢复行为和部署配置来源。RFC 不规定通用数值，不在规范中伪造常量。依据：RFC6455 §10.4。

**WS07｜Extensions/compression｜Skill MUST。** 只启用明确协商的 extension/subprotocol，按其定义处理 RSV bits、context takeover 与解压限制；RSV 未经协商使用时按 RFC fail connection。压缩文档涵盖 decompressed size/CPU 限额和跨用户秘密与攻击者可控内容同压缩的风险；缺目标库/配置证据时不默认开 permessage-deflate。依据：RFC6455 §5.2、§9。

**WS08｜安全和输入｜规范 MUST + Skill MUST。** 服务器验证所有 client payload，即使 TLS/Origin/subprotocol 已验证；浏览器共享 cookie 场景校验 Origin；设置消息与连接限额并防止持久重连风暴。服务器→客户端须按用户/租户授权过滤每条消息；不能因握手时已认证就忽略权限撤销。依据：RFC6455 §10。
