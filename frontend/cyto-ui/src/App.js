import React, { useEffect, useState } from "react";
import SummaryTable from "./components/SummaryTable";
import SampleForm from "./components/SampleForm";
import FilterPanel from "./components/FilterPanel";
import BoxplotView from "./components/BoxplotView";
import StatsReport from "./components/StatsReport";

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Immune Cell Explorer</h1>
      <SampleForm onSuccess={handleRefresh} />
      <SummaryTable refreshTrigger={refreshTrigger} />
      <FilterPanel />
      <BoxplotView refreshTrigger={refreshTrigger} />
      <StatsReport refreshTrigger={refreshTrigger} />
    </div>
  );
}

export default App;
