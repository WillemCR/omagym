use rust_02_config::{parse_config, ConfigError, ErrorKind};
use std::collections::BTreeMap;
#[test]
fn blank_and_comments() { assert_eq!(parse_config("  \n # comment\n\r\n").unwrap(), BTreeMap::new()); }
#[test]
fn trims_and_preserves_values() { let expected = BTreeMap::from([("HOST".into(), "localhost".into()), ("token".into(), "a=b # literal".into()), ("_empty2".into(), "".into())]); assert_eq!(parse_config(" HOST = localhost\r\ntoken=a=b # literal\n_empty2= ").unwrap(), expected); }
#[test]
fn missing_separator_has_line() { assert_eq!(parse_config("# comment\n\nvalid=yes\nbroken"), Err(ConfigError { line: 4, kind: ErrorKind::InvalidLine })); }
#[test]
fn invalid_keys() { for key in ["", "2host", "two words", "host-name", "é", "a.b"] { assert_eq!(parse_config(&format!("ok=yes\n{key}=x")), Err(ConfigError { line: 2, kind: ErrorKind::InvalidKey })); } }
#[test]
fn duplicate_and_case_sensitivity() { assert_eq!(parse_config("a=one\na=two"), Err(ConfigError { line: 2, kind: ErrorKind::DuplicateKey })); assert_eq!(parse_config("a=one\nA=two").unwrap().len(), 2); }
#[test]
fn first_error_wins() { assert_eq!(parse_config("a=x\na=y\nno separator"), Err(ConfigError { line: 2, kind: ErrorKind::DuplicateKey })); assert_eq!(parse_config("bad key=x\na=x\na=y"), Err(ConfigError { line: 1, kind: ErrorKind::InvalidKey })); }
