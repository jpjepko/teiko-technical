import React, { useEffect, useState } from "react";

export default function StatsReport({ refreshTrigger }) {
  const [stats, setStats] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/compare-stats");
        const json = await res.json();
        setStats(json[0]); // Assuming outer array wrapper as in your example
      } catch (err) {
        console.error("Failed to fetch significance stats:", err);
      }
    };

    fetchStats();
  }, [refreshTrigger]);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Statistical Significance Report</h3>
      <table className="min-w-full border border-gray-300 text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-2 py-1">Population</th>
            <th className="border px-2 py-1">p-value</th>
            <th className="border px-2 py-1">Significant?</th>
          </tr>
        </thead>
        <tbody>
          {stats.map(({ population, p_value, significant }) => (
            <tr key={population}>
              <td className="border px-2 py-1">{population}</td>
              <td className="border px-2 py-1">{p_value.toFixed(4)}</td>
              <td
                className={`border px-2 py-1 font-semibold ${
                  significant ? "text-green-600" : "text-gray-500"
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
