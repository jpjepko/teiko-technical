import React, { useEffect, useState, useCallback } from "react";
import SummaryTable from "./components/SummaryTable";
import SampleForm from "./components/SampleForm";
import FilterPanel from "./components/FilterPanel";
import BoxplotView from "./components/BoxplotView";
import StatsReport from "./components/StatsReport";

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
      <FilterPanel />
      <BoxplotView refreshTrigger={refreshTrigger} />
      <StatsReport refreshTrigger={refreshTrigger} />
    </div>
  );
}

export default App;
