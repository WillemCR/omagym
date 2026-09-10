use std::collections::BTreeMap;
#[derive(Debug, PartialEq, Eq)]
pub enum ErrorKind { InvalidLine, InvalidKey, DuplicateKey }
#[derive(Debug, PartialEq, Eq)]
pub struct ConfigError { pub line: usize, pub kind: ErrorKind }

pub fn parse_config(_text: &str) -> Result<BTreeMap<String, String>, ConfigError> {
    todo!("Read and validate the configuration")
}
