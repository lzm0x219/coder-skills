//! 候选扩展接口；仅供设计期编译，不含存储实现。

use std::error::Error;
use std::io::Read;

/// 仅包含打开阶段的失败。读句柄后的错误由 `Read` 报告。
#[derive(Debug)]
#[non_exhaustive]
pub enum OpenError {
    InvalidKey,
    Backend(Box<dyn Error + Send + Sync>),
}

/// 由第三方实现的读取能力。新增必需方法会破坏实现者。
pub trait BlobStore: Send + Sync {
    /// 每次调用可能发生 I/O；`None` 表示键合法但对象不存在。
    /// 成功时将读句柄的所有权转移给调用方。
    fn open(&self, key: &str) -> Result<Option<Box<dyn Read + Send>>, OpenError>;
}
