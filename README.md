# teiko-technical

# Requirements
* Python >= 3.13

## Usage
Create virtual environment, install Python dependencies, and run Flask backend (for dev environment):
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

## Code Structure
The structure is as follows:
```
teiko-technical/
├── backend/
│   ├── app.py
│   ├── data/
│   │   └── cell-count.csv
│   ├── db/
│   │   ├── database.db
│   │   └── schema.sql
│   ├── env/
│   ├── requirements.txt
│   └── util/
│       ├── db.py
│       └── __init__.py
├── frontend
│   └── cyto-ui/
│       ├── node_modules/
│       ├── package.json
│       ├── package-lock.json
│       ├── public/
│       │   ├── index.html
│       │   └── manifest.json
│       ├── README.md
│       ├── src/
│       │   ├── components/
│       │   │   ├── BoxplotView.jsx
│       │   │   ├── FilterPanel.jsx
│       │   │   ├── SampleForm.jsx
│       │   │   ├── StatsReport.jsx
│       │   │   └── SummaryTable.jsx
│       │   ├── App.js
│       │   ├── index.css
│       │   └── index.js
│       └── tailwind.config.js
└── README.md
```

The backend and frontend are stored in separate directories.

### Backend
The backend is kept simple. All the API routes are kept in `app.py`, and all database querying and operations are separated in `util/db.py`.

#### Endpoints
* `GET /samples`
  * TODO

### Frontend
The React frontend is in the `frontend/cyto-ui` dir. The main view is stored in `src/App.js`, and each component is separated into its own `.jsx` file in `src/components/`. Each component manages its own state, but the main `App` component uses a `refreshTrigger` state variable, which is incremented for every successful form submit. `App` passes it to other components as a prop, which in turn use it in their `useEffect` hooks to refresh their view.

## Extensions
* Inserting samples currently requires all fields. If the subject exists, the subject metadata fields are ignored. It would be easier for the user if the app first checked if the subject exists, thus not requiring subject metadata (at the cost of increased code complexity).
* Better error handling, many components simply return nothing rather than inform user of an error.
* For a production-ready deployment, `flask run` should not be used, configuring something like `gunicorn` for the backend and `Nginx` for the frontend would help. And use `python-dotenv` instead of globals for the config.
