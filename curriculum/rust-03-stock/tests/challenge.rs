use rust_03_stock::{apply_batch, Change, BatchError, ErrorKind};
use std::collections::BTreeMap;
fn c(sku: &str, delta: i64) -> Change { Change { sku: sku.into(), delta } }
#[test]
fn successful_batch_is_ordered() { let mut s = BTreeMap::from([("book".into(), 4)]); assert_eq!(apply_batch(&mut s, &[c("book",-3),c("pen",6),c("book",2)]), Ok(())); assert_eq!(s, BTreeMap::from([("book".into(),3),("pen".into(),6)])); }
#[test]
fn underflow_rolls_back_everything() { let mut s=BTreeMap::from([("book".into(),4)]); let old=s.clone(); assert_eq!(apply_batch(&mut s,&[c("new",5),c("book",-5),c("book",10)]),Err(BatchError{index:1,kind:ErrorKind::Underflow})); assert_eq!(s,old); }
#[test]
fn overflow_and_extreme_deltas() { for delta in [1, i64::MAX] { let mut s=BTreeMap::from([("x".into(),u32::MAX)]); let old=s.clone(); assert_eq!(apply_batch(&mut s,&[c("x",delta)]),Err(BatchError{index:0,kind:ErrorKind::Overflow})); assert_eq!(s,old); } let mut s=BTreeMap::new(); assert_eq!(apply_batch(&mut s,&[c("x",i64::MIN)]),Err(BatchError{index:0,kind:ErrorKind::Underflow})); assert!(s.is_empty()); }
#[test]
fn invalid_skus_are_atomic() { for sku in ["", " x", "x ", "\tx"] { let mut s=BTreeMap::new(); assert_eq!(apply_batch(&mut s,&[c("good",1),c(sku,-1)]),Err(BatchError{index:1,kind:ErrorKind::InvalidSku})); assert!(s.is_empty()); } }
#[test]
fn zero_entries_and_case() { let mut s=BTreeMap::new(); assert_eq!(apply_batch(&mut s,&[c("x",2),c("x",-2),c("X",0),c("inner space",1)]),Ok(())); assert_eq!(s,BTreeMap::from([("x".into(),0),("X".into(),0),("inner space".into(),1)])); }
#[test]
fn empty_batch_is_noop() { let mut s=BTreeMap::from([("x".into(),9)]); let old=s.clone(); assert_eq!(apply_batch(&mut s,&[]),Ok(())); assert_eq!(s,old); }
