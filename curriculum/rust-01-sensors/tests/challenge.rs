use rust_01_sensors::{summarize, Report};
#[test]
fn empty_has_no_report() { assert_eq!(summarize(&[]), None); }
#[test]
fn single_reading() { assert_eq!(summarize(&[7]), Some(Report { count: 1, min: 7, max: 7, total: 7, rising: 0 })); }
#[test]
fn mixed_readings() { let input = [-2, 4, 4, -8, 9]; assert_eq!(summarize(&input), Some(Report { count: 5, min: -8, max: 9, total: 7, rising: 2 })); assert_eq!(input, [-2,4,4,-8,9]); }
#[test]
fn large_total() { assert_eq!(summarize(&[i32::MAX, i32::MAX]).unwrap().total, 4_294_967_294); assert_eq!(summarize(&[i32::MIN, i32::MIN]).unwrap().total, -4_294_967_296); }
#[test]
fn descending_and_equal() { assert_eq!(summarize(&[3,3,2,1]).unwrap().rising, 0); assert_eq!(summarize(&[-5,-4,-3]).unwrap().rising, 2); }
