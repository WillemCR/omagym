use std::collections::BTreeMap;
#[derive(Debug, Clone)]
pub struct Change { pub sku: String, pub delta: i64 }
#[derive(Debug, PartialEq, Eq)]
pub enum ErrorKind { InvalidSku, Underflow, Overflow }
#[derive(Debug, PartialEq, Eq)]
pub struct BatchError { pub index: usize, pub kind: ErrorKind }

pub fn apply_batch(_stock: &mut BTreeMap<String, u32>, _changes: &[Change]) -> Result<(), BatchError> {
    todo!("Apply the whole batch or leave stock unchanged")
}
