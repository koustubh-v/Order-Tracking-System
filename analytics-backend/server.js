const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const http = require('http');
const { Server } = require('socket.io');
const { Kafka } = require('kafkajs');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:postgres@postgres:5432/analytics'
});

const kafka = new Kafka({
  clientId: 'analytics-backend',
  brokers: [process.env.KAFKA_BROKER || 'kafka:9092']
});

const consumer = kafka.consumer({ groupId: 'analytics-backend-group' });

async function runKafka() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'order_events', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const event = JSON.parse(message.value.toString());
      io.emit('order_update', event);
    },
  });
}

runKafka().catch(console.error);

io.on('connection', (socket) => {
  socket.on('disconnect', () => {});
});

app.get('/analytics/orders-per-hour', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT TO_CHAR(hour_bucket, 'YYYY-MM-DD HH24:00') as hour, COUNT(*) as count 
      FROM fact_orders 
      GROUP BY hour_bucket 
      ORDER BY hour_bucket ASC 
      LIMIT 24
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/status-distribution', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT status, COUNT(*) as count 
      FROM fact_orders 
      GROUP BY status
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/average-delivery-time', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT AVG(delivery_time_seconds) as avg_time 
      FROM delivery_metrics
    `);
    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/sales-trend', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        hour_bucket,
        SUM(amount) OVER (ORDER BY hour_bucket) as running_total,
        AVG(amount) OVER (ORDER BY hour_bucket ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) as moving_avg
      FROM (
        SELECT hour_bucket, SUM(amount) as amount
        FROM fact_orders
        GROUP BY hour_bucket
      ) sub
      ORDER BY hour_bucket DESC
      LIMIT 20
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/top-categories', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        COALESCE(p.main_category, 'Unknown') as main_category,
        COUNT(f.id) as order_count,
        SUM(f.amount) as total_revenue
      FROM fact_orders f
      LEFT JOIN dim_products p ON f.product_id = p.product_id
      GROUP BY p.main_category
      ORDER BY total_revenue DESC
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/recent-orders', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT order_id, user_id, status, amount, event_time 
      FROM fact_orders 
      ORDER BY event_time DESC 
      LIMIT 10
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/analytics/summary', async (req, res) => {
    try {
        const totalReq = await pool.query('SELECT COUNT(DISTINCT order_id) as total FROM fact_orders');
        const deliveredReq = await pool.query("SELECT COUNT(DISTINCT order_id) as delivered FROM fact_orders WHERE status = 'DELIVERED'");
        const pendingReq = await pool.query("SELECT COUNT(DISTINCT order_id) as pending FROM fact_orders WHERE status != 'DELIVERED' AND status != 'CANCELLED'");
        
        res.json({
            total: parseInt(totalReq.rows[0].total) || 0,
            delivered: parseInt(deliveredReq.rows[0].delivered) || 0,
            pending: parseInt(pendingReq.rows[0].pending) || 0
        });
    } catch (error) {
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(`Analytics API listening on port ${PORT}`);
});
