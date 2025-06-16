# teiko-technical

# Requirements
* Python >= 3.13

## Usage
Create virtual environment, install Python dependencies, and run Flask backend:
```sh
$ cd backend/
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ flask run
```

Install `npm` dependencies and run
```sh
$ cd frontend/cyto-ui
$ npm install
$ npm start
```

## Schema
The schema is defined in `backend/db/schema.sql`.
### `subjects`
| Field        | Type    | Attributes  |
| ------------ | ------- | ----------- |
| `subject_id` | text    | primary key |
| `project`    | text    |             |
| `condition`  | text    |             |
| `age`        | integer |             |
| `sex`        | text    |             |

The `subjects` table stores metadata about each human subject in the data. Isolating the subjects into their own table avoids storing duplicated data, making it more efficient to query on subject-level data (like age or project), especially when scaled to larger datasets.

### `samples`
| Field                       | Type    | Attributes                   |
| --------------------------- | ------- | ---------------------------- |
| `sample_id`                 | text    | primary key                  |
| `subject_id`                | text    | ref to `subjects.subject_id` |
| `treatment`                 | text    |                              |
| `response`                  | text    |                              |
| `sample_type`               | text    |                              |
| `time_from_treatment_start` | integer |                              |

The `samples` table stores metadata about every sample in the data. Again, duplication is avoided by only storing relevant data to each sample, and it is linked to the `subjects` tables with a relation to `subject_id`. This is particularly helpful when deleting a sample, as it would not desirable to delete subject metadata if there are still other `samples` linked to them in the data. Efficient insertion/removal is key to scalability.

### `cell_counts`
| Field        | Type    | Attributes                 |
| ------------ | ------- | -------------------------- |
| `id`         | integer | primary key                |
| `sample_id`  | text    | ref to `samples.sample_id` |
| `population` | text    |                            |
| `count`      | integer |                            |

The `cell_counts` table stores the counts/populations of each cell-type, with a relation to the `samples` table, as each cell count is tied to a specific example. Only necessary information is stored; other fields of interest (like total count across a sample) can be easily computed with a SQL query. Storing just what is needed also aids in scalability, minimizing storing and managing unnecessary data.

In general, the relations/foreign key constraints are helpful in avoiding invalid data states, as the schema requires those keys to exist in other tables.

## Extensions
* TODO.
