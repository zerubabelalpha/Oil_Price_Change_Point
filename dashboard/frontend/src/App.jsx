import React, { useState, useEffect } from 'react';
import axios from 'axios';
import OilPriceChart from './components/OilPriceChart';
import StatsPanel from './components/StatsPanel';
import EventList from './components/EventList';
import { Filter, RefreshCw } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [prices, setPrices] = useState([]);
  const [changePoint, setChangePoint] = useState(null);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pricesRes, cpRes, eventsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/historical-prices`),
        axios.get(`${API_BASE_URL}/change-points`),
        axios.get(`${API_BASE_URL}/events`),
        axios.get(`${API_BASE_URL}/stats`)
      ]);

      setPrices(pricesRes.data);
      setChangePoint(cpRes.data);
      setEvents(eventsRes.data);
      setStats(statsRes.data);

      if (pricesRes.data.length > 0) {
        setDateRange({
          start: pricesRes.data[0].Date,
          end: pricesRes.data[pricesRes.data.length - 1].Date
        });
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredPrices = prices.filter(p =>
    (!dateRange.start || p.Date >= dateRange.start) &&
    (!dateRange.end || p.Date <= dateRange.end)
  );

  const handleEventClick = (event) => {
    setSelectedEvent(event === selectedEvent ? null : event);
    // If we wanted to drill down or highlight, we'd do it here
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <RefreshCw className="animate-spin" size={48} color="#38bdf8" />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Brent Oil Price Analysis</h1>
          <p style={{ color: '#94a3b8', margin: '0.5rem 0 0' }}>Bayesian Change Point Detection & Event Correlation</p>
        </div>
        <div className="filters-container">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={16} color="#94a3b8" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            />
            <span style={{ color: '#94a3b8' }}>to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            />
          </div>
        </div>
      </header>

      <StatsPanel stats={stats} />

      <main className="main-content">
        <OilPriceChart
          data={filteredPrices}
          changePoint={changePoint}
          events={events}
          onEventClick={handleEventClick}
        />
        <EventList
          events={events}
          onEventClick={handleEventClick}
          selectedEvent={selectedEvent}
        />
      </main>

      <footer style={{ marginTop: 'auto', textAlign: 'center', padding: '2rem 0', color: '#64748b', fontSize: '0.875rem' }}>
        Antigravity Analytics Platform &copy; 2026 | Data: Brent Crude Oil Spot Price
      </footer>
    </div>
  );
}

export default App;
