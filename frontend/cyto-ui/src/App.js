import React, { useEffect, useState, useCallback } from "react";
import SummaryTable from "./components/SummaryTable";
import SampleForm from "./components/SampleForm";

function App() {
  const [summaryData, setSummaryData] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchSummary = useCallback(async () => {
    try {
      const res = await fetch("/summary");
      const data = await res.json();
      setSummaryData(data);
    } catch (error) {
      console.error("error fetching summary: ", error);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary, refreshTrigger]);

  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Immune Cell Explorer</h1>
      <SampleForm onSuccess={handleRefresh} />
      <SummaryTable data={summaryData} />
    </div>
  )
  /*
  return (
    <div className="p-4">
      <SummaryTable />

      <h2 className="text-xl font-semibold mb-2">Filter Samples</h2>
      <form onSubmit={handleFilter} className="grid grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          name="condition"
          placeholder="Condition"
          value={formData.condition}
          onChange={handleChange}
          className="border p-2"
        />
        <input
          type="text"
          name="treatment"
          placeholder="Treatment"
          value={formData.treatment}
          onChange={handleChange}
          className="border p-2"
        />
        <input
          type="number"
          name="time_from_treatment_start"
          placeholder="Time"
          value={formData.time_from_treatment_start}
          onChange={handleChange}
          className="border p-2"
        />
        <input
          type="text"
          name="sample_type"
          placeholder="Sample Type"
          value={formData.sample_type}
          onChange={handleChange}
          className="border p-2"
        />
        <button type="submit" className="col-span-2 bg-blue-600 text-white py-2 rounded">
          Run Filter
        </button>
      </form>

      {filtered.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Filtered Results</h2>
          <table className="table-auto w-full border">
            <thead className="bg-gray-100">
              <tr>
                <th className="border px-4 py-2">Sample ID</th>
                <th className="border px-4 py-2">Population</th>
                <th className="border px-4 py-2">Count</th>
                <th className="border px-4 py-2">Response</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, i) => (
                <tr key={i}>
                  <td className="border px-4 py-2">{row.sample_id}</td>
                  <td className="border px-4 py-2">{row.population}</td>
                  <td className="border px-4 py-2">{row.count}</td>
                  <td className="border px-4 py-2">{row.response}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
  */
}

export default App;
