import React, { useState } from "react";

export default function FilterPanel() {
  const [sampleType, setSampleType] = useState("PBMC");
  const [condition, setCondition] = useState("melanoma");
  const [treatment, setTreatment] = useState("tr1");
  const [time, setTime] = useState(0);
  const [results, setResults] = useState(null);

  const handleQuery = async () => {
    const params = new URLSearchParams({
      sample_type: sampleType,
      condition,
      treatment,
      time_from_treatment_start: time,
    });

    try {
      const res = await fetch(`/filter?${params}`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Error fetching filter results:", err);
    }
  };

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-2">Filter Panel</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <input
          type="text"
          value={sampleType}
          onChange={(e) => setSampleType(e.target.value)}
          className="border px-2 py-1 rounded"
          placeholder="Sample Type"
        />
        <input
          type="text"
          value={condition}
          onChange={(e) => setCondition(e.target.value)}
          className="border px-2 py-1 rounded"
          placeholder="Condition"
        />
        <input
          type="text"
          value={treatment}
          onChange={(e) => setTreatment(e.target.value)}
          className="border px-2 py-1 rounded"
          placeholder="Treatment"
        />
        <input
          type="number"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          className="border px-2 py-1 rounded"
          placeholder="Time from Treatment Start"
        />
      </div>

      <button
        onClick={handleQuery}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Query
      </button>

      {results && (
        <div className="mt-4 text-sm space-y-2">
          <div>
            <strong>Samples per Project:</strong>{" "}
            {Object.entries(results.num_samples_per_project)
              .map(([project, count]) => `${project}: ${count}`)
              .join(", ")}
          </div>
          <div>
            <strong>Response Counts:</strong>{" "}
            {Object.entries(results.response_counts)
              .map(([resp, count]) => `${resp === "y" ? "Responders" : "Non-responders"}: ${count}`)
              .join(", ")}
          </div>
          <div>
            <strong>Sex Counts:</strong>{" "}
            {Object.entries(results.sex_counts)
              .map(([sex, count]) => `${sex}: ${count}`)
              .join(", ")}
          </div>
          <div>
            <strong>Sample IDs:</strong>{" "}
            {results.sample_ids.join(", ")}
          </div>
        </div>
      )}
    </div>
  );
}
