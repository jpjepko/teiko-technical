import React, { useEffect, useState } from "react";

export default function SummaryTable({ data }) {
  if (!data) return <p>loading summary...</p>;
  if (data.length === 0) return <p>no summary data available.</p>;

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
          {data.map((row, idx) => (
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
