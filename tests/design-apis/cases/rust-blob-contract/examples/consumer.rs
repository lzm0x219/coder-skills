//! 编译期调用点；本文件不运行真实存储。

use blob_contract_design::{BlobStore, OpenError};
use std::io::{self, Read};

#[derive(Debug)]
pub enum ReadPrefixError {
    Open(OpenError),
    Read(io::Error),
}

pub fn read_prefix(store: &dyn BlobStore, key: &str) -> Result<Option<Vec<u8>>, ReadPrefixError> {
    let mut reader = match store.open(key).map_err(ReadPrefixError::Open)? {
        Some(reader) => reader,
        None => return Ok(None),
    };

    let mut bytes = [0_u8; 4096];
    let count = reader.read(&mut bytes).map_err(ReadPrefixError::Read)?;
    Ok(Some(bytes[..count].to_vec()))
}

fn main() {}
