import React, { useEffect, useState } from "react";

export default function SummaryTable({ refreshTrigger }) {
  const [summary, setSummary] = useState([]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch("/summary");
        const json = await res.json();
        setSummary(json);
      } catch (err) {
        console.error("failed to fetch summmary: ", err);
      }
    };

    fetchSummary();
  }, [refreshTrigger]);

  return (
    <div className="overflow-x-auto mt-4">
      <h2 className="text-lg font-semibold mb-2">Summary Table</h2>
      <table className="min-w-full table-auto border border-gray-300">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 border">Sample ID</th>
            <th className="px-4 py-2 border">Population</th>
            <th className="px-4 py-2 border">Count</th>
            <th className="px-4 py-2 border">Total Count</th>
            <th className="px-4 py-2 border">Relative Frequency (%)</th>
          </tr>
        </thead>
        <tbody>
          {summary.map((row, idx) => (
            <tr key={idx} className="text-center hover:bg-gray-50">
              <td className="px-4 py-2 border">{row.sample_id}</td>
              <td className="px-4 py-2 border">{row.population}</td>
              <td className="px-4 py-2 border">{row.count}</td>
              <td className="px-4 py-2 border">{row.total_count}</td>
              <td className="px-4 py-2 border">
                {row.relative_frequency.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
