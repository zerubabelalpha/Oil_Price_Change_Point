import React, { useMemo } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceArea,
    ReferenceLine,
    Scatter,
    ComposedChart
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="custom-tooltip">
                <p className="label">{`Date: ${label}`}</p>
                <p className="price" style={{ color: '#38bdf8', fontWeight: 'bold' }}>
                    {`Price: $${payload[0].value.toFixed(2)}`}
                </p>
            </div>
        );
    }
    return null;
};

const OilPriceChart = ({ data, changePoint, events, onEventClick }) => {
    if (!data || data.length === 0) return <div>Loading chart...</div>;

    return (
        <div className="chart-container">
            <h3 style={{ marginBottom: '1rem' }}>Historical Price Analysis</h3>
            <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis
                        dataKey="Date"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        minTickGap={50}
                    />
                    <YAxis
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        domain={['auto', 'auto']}
                        tickFormatter={(val) => `$${val}`}
                    />
                    <Tooltip content={<CustomTooltip />} />

                    {/* Highlight Change Point CI Area */}
                    {changePoint && changePoint.ci_lower && changePoint.ci_upper && (
                        <ReferenceArea
                            x1={changePoint.ci_lower}
                            x2={changePoint.ci_upper}
                            fill="#ef4444"
                            fillOpacity={0.15}
                        />
                    )}

                    {/* Detected Change Point Line */}
                    {changePoint && changePoint.change_point_date && (
                        <ReferenceLine
                            x={changePoint.change_point_date}
                            stroke="#ef4444"
                            strokeDasharray="5 5"
                            label={{ value: 'Change Point', fill: '#ef4444', position: 'top', fontSize: 10 }}
                        />
                    )}

                    {/* Price Line */}
                    <Line
                        type="monotone"
                        dataKey="Price"
                        stroke="#38bdf8"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, strokeWidth: 0 }}
                    />

                    {/* Event Markers (using ReferenceLines for simplicity/visual impact) */}
                    {events.map((event, idx) => (
                        <ReferenceLine
                            key={idx}
                            x={event.Start_Date}
                            stroke="#94a3b8"
                            strokeOpacity={0.4}
                            onClick={() => onEventClick(event)}
                            isFront
                        />
                    ))}
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
};

export default OilPriceChart;
