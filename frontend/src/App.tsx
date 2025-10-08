import React from 'react';
import AssetList from './components/AssetList';
import AlertsDashboard from './components/AlertsDashboard';
import './App.css';

function App() {
  return (
    <div className="grid grid-cols-5 h-screen bg-gray-900 text-white font-sans">
      <div className="col-span-1 border-r border-gray-700">
        <AssetList />
      </div>
      <div className="col-span-4">
        <AlertsDashboard />
      </div>
    </div>
  );
}

export default App;
