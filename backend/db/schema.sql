CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,
    project TEXT,
    condition TEXT,
    age INTEGER,
    sex TEXT
);

CREATE TABLE samples (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT REFERENCES subjects(subject_id),
    treatment TEXT,
    response TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER
);

CREATE TABLE cell_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id TEXT REFERENCES samples(sample_id),
    population TEXT CHECK(population IN ('b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte')),
    count INTEGER
);
