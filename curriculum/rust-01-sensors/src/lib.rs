#[derive(Debug, PartialEq, Eq)]
pub struct Report {
    pub count: usize,
    pub min: i32,
    pub max: i32,
    pub total: i64,
    pub rising: usize,
}

pub fn summarize(_readings: &[i32]) -> Option<Report> {
    todo!("Build your sensor report")
}
