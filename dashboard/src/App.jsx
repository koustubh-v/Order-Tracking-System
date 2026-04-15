import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { Activity, Package, Clock, CheckCircle } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';
const socket = io(API_URL);

// Chart Colors based on dark theme
const COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171'];

function App() {
  const [summary, setSummary] = useState({ total: 0, delivered: 0, pending: 0 });
  const [hourlyData, setHourlyData] = useState([]);
  const [statusData, setStatusData] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [avgDeliveryTime, setAvgDeliveryTime] = useState(0);

  const fetchDashboardData = async () => {
    try {
      const [sumRes, hourlyRes, statusRes, recentRes, avgRes] = await Promise.all([
        fetch(`${API_URL}/analytics/summary`),
        fetch(`${API_URL}/analytics/orders-per-hour`),
        fetch(`${API_URL}/analytics/status-distribution`),
        fetch(`${API_URL}/analytics/recent-orders`),
        fetch(`${API_URL}/analytics/average-delivery-time`)
      ]);

      setSummary(await sumRes.json());

      const hd = await hourlyRes.json();
      setHourlyData(hd.map(d => ({ name: d.hour.split(' ')[1], orders: parseInt(d.count) })));

      const sd = await statusRes.json();
      setStatusData(sd.map(d => ({ name: d.status, value: parseInt(d.count) })));

      setRecentOrders(await recentRes.json());
      
      const ad = await avgRes.json();
      setAvgDeliveryTime(ad.avg_time ? Math.round(parseFloat(ad.avg_time) / 60) : 0); // convert secs to mins
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    socket.on('order_update', (data) => {
      console.log('Real-time update received:', data);
      // Fetch full refresh for simplicity in demo
      fetchDashboardData();
    });

    return () => {
      socket.off('order_update');
    };
  }, []);

  return (
    <div>
      <header className="app-header">
        <div className="app-title">
          <Activity size={28} color="#38bdf8" />
          Real-Time Order Tracking
        </div>
        <div style={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem' }}>
          <span className="live-indicator"></span>
          Live Environment
        </div>
      </header>

      <main className="dashboard-container">
        
        {/* Top Metrics Cards */}
        <section className="metrics-grid">
          <div className="glass-panel metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="metric-title">Total Orders</div>
              <Package size={20} color="#818cf8" />
            </div>
            <div className="metric-value">{summary.total}</div>
          </div>
          
          <div className="glass-panel metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="metric-title">Orders Delivered</div>
              <CheckCircle size={20} color="#34d399" />
            </div>
            <div className="metric-value">{summary.delivered}</div>
          </div>
          
          <div className="glass-panel metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="metric-title">Pending Orders</div>
              <Activity size={20} color="#fbbf24" />
            </div>
            <div className="metric-value">{summary.pending}</div>
          </div>
          
          <div className="glass-panel metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="metric-title">Avg Delivery Time</div>
              <Clock size={20} color="#f87171" />
            </div>
            <div className="metric-value">{avgDeliveryTime} <span style={{fontSize: '1.25rem', color: 'var(--text-secondary)'}}>min</span></div>
          </div>
        </section>

        {/* Charts */}
        <section className="charts-grid">
          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 600 }}>Orders Velocity</h3>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" stroke="var(--text-secondary)" />
                  <YAxis stroke="var(--text-secondary)" />
                  <Tooltip />
                  <Line type="monotone" dataKey="orders" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4, fill: '#38bdf8' }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 600 }}>Status Distribution</h3>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-\${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* Recent Orders Table */}
        <section className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 600 }}>Live Feed (Recent Orders)</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer ID</th>
                  <th>Amount</th>
                  <th>Timestamp</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentOrders.map((order) => (
                  <tr key={order.order_id}>
                    <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{order.order_id.substring(0,8)}...</td>
                    <td>{order.user_id}</td>
                    <td>\${parseFloat(order.amount).toFixed(2)}</td>
                    <td>{new Date(order.event_time).toLocaleTimeString()}</td>
                    <td>
                      <span className={`badge \${order.status.toLowerCase()}`}>
                        {order.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {recentOrders.length === 0 && (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                      No orders to display. Waiting for live events...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;
