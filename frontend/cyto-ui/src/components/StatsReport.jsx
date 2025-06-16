import React, { useEffect, useState } from "react";

export default function StatsReport({ refreshTrigger }) {
  const [stats, setStats] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/compare-stats");
        const json = await res.json();
        setStats(json);
      } catch (err) {
        console.error("Failed to fetch significance stats:", err);
      }
    };

    fetchStats();
  }, [refreshTrigger]);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Statistical Significance Report</h3>
      <table className="min-w-full table-auto border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="px-4 py-2 border">Population</th>
            <th className="px-4 py-2 border">p-value</th>
            <th className="px-4 py-2 border">Significant?</th>
          </tr>
        </thead>
        <tbody>
          {stats.map(({ population, p_value, significant }) => (
            <tr key={population}>
              <td className="px-4 py-2 border">{population}</td>
              <td className="px-4 py-2 border">
                {p_value != null ? p_value.toFixed(4) : "N/A"}
              </td>
              <td
                className={`border px-2 py-1 font-semibold ${
                  significant ? "text-green-600" : "text-red-600"
                }`}
              >
                {significant ? "Yes" : "No"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
