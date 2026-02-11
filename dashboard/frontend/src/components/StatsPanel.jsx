import React from 'react';
import { TrendingUp, TrendingDown, Target, Zap } from 'lucide-react';

const StatCard = ({ label, value, icon: Icon, color, prefix = '', suffix = '' }) => (
    <div className="stat-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="stat-label">{label}</span>
            <Icon size={18} color={color} />
        </div>
        <div className="stat-value">
            {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </div>
    </div>
);

const StatsPanel = ({ stats }) => {
    if (!stats) return null;

    return (
        <div className="stats-grid">
            <StatCard
                label="Mean Price (Before CP)"
                value={stats.mu_before}
                icon={TrendingUp}
                color="#38bdf8"
                prefix="$"
            />
            <StatCard
                label="Mean Price (After CP)"
                value={stats.mu_after}
                icon={TrendingUp}
                color="#22c55e"
                prefix="$"
            />
            <StatCard
                label="Price Shift"
                value={stats.price_change}
                icon={stats.price_change > 0 ? TrendingUp : TrendingDown}
                color={stats.price_change > 0 ? '#22c55e' : '#ef4444'}
                prefix="$"
            />
            <StatCard
                label="Change %"
                value={stats.price_change_pct}
                icon={Zap}
                color="#f59e0b"
                suffix="%"
            />
        </div>
    );
};

export default StatsPanel;
