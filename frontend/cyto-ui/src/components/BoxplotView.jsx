import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

export default function BoxplotView({ refreshTrigger }) {
  const [plotData, setPlotData] = useState([]);

  useEffect(() => {
    const fetchCompareData = async () => {
      try {
        const res = await fetch("/compare");
        const raw = await res.json();

        // Organize data by population -> response -> list of percentages
        const grouped = {}; // { b_cell: { y: [], n: [] }, ... }

        for (const row of raw) {
          const { population, response } = row;
          const freq = row.percentage ?? row.relative_frequency ?? 0;

          if (!grouped[population]) grouped[population] = { y: [], n: [] };
          grouped[population][response]?.push(freq);
        }

        // Create one trace per response ('y' and 'n'), each with x and y arrays
        const responses = ['y', 'n'];
        const traces = responses.map((resp) => {
          return {
            type: 'box',
            name: resp === 'y' ? 'Responders' : 'Non-responders',
            x: [], // population name repeated for each data point
            y: [],
            boxpoints: "all",
            jitter: 0.3,
            pointpos: -1.8,
            marker: {color: resp === 'y' ? "#3D9970" : "#FF4136"}
          };
        });

        // Populate traces
        for (const population in grouped) {
          for (const resp of responses) {
            const values = grouped[population][resp] || [];
            traces[resp === 'y' ? 0 : 1].x.push(...Array(values.length).fill(population));
            traces[resp === 'y' ? 0 : 1].y.push(...values);
          }
        }

        setPlotData(traces);
      } catch (err) {
        console.error("Failed to load comparison data:", err);
      }
    };

    fetchCompareData();
  }, [refreshTrigger]);

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-2">Boxplot: Cell Frequency by Response</h2>
      <Plot
        data={plotData}
        layout={{
          title: "Relative Frequencies by Cell Type and Response",
          yaxis: {
            title: "Relative Frequency (%)",
            zeroline: false,
          },
          boxmode: "group",
          margin: { t: 40, b: 120 },
        }}
        style={{ width: "100%", height: "500px" }}
      />
    </div>
  );
}
