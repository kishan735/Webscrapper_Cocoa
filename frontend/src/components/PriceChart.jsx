import React, { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts'
import { format } from 'date-fns'

const periodOptions = [
  { value: '7d', label: '7D' },
  { value: '30d', label: '1M' },
  { value: '90d', label: '3M' },
  { value: '1y', label: '1Y' },
]

function PriceChart({ chartData, loading, period, onPeriodChange }) {
  if (loading) {
    return (
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <div className="skeleton h-6 w-32"></div>
          <div className="skeleton h-8 w-48"></div>
        </div>
        <div className="skeleton h-64 w-full"></div>
      </div>
    )
  }

  const data = chartData?.data || []
  const range = chartData?.range || { min: 0, max: 0 }

  // Format data for chart
  const formattedData = data.map(item => ({
    ...item,
    formattedDate: format(new Date(item.timestamp), 'MMM d'),
    formattedPrice: `$${item.price.toLocaleString()}`,
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-slate-400 text-sm">{payload[0].payload.formattedDate}</p>
          <p className="text-white font-bold text-lg">{payload[0].payload.formattedPrice}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-semibold text-white">Price History</h3>
        <div className="flex space-x-1 bg-slate-700 rounded-lg p-1">
          {periodOptions.map(option => (
            <button
              key={option.value}
              onClick={() => onPeriodChange(option.value)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                period === option.value
                  ? 'bg-violet-600 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {data.length > 0 ? (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={formattedData}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="formattedDate"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                tickLine={{ stroke: '#334155' }}
                axisLine={{ stroke: '#334155' }}
              />
              <YAxis
                domain={[range.min * 0.98, range.max * 1.02]}
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                tickLine={{ stroke: '#334155' }}
                axisLine={{ stroke: '#334155' }}
                tickFormatter={value => `$${(value / 1000).toFixed(1)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#8b5cf6"
                strokeWidth={2}
                fill="url(#priceGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-64 flex items-center justify-center text-slate-400">
          No price data available for this period
        </div>
      )}

      {/* Stats row */}
      {data.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-700">
          <div className="text-center">
            <p className="text-slate-400 text-sm">Low</p>
            <p className="text-white font-semibold">${range.min?.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-slate-400 text-sm">Average</p>
            <p className="text-white font-semibold">${range.avg?.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-slate-400 text-sm">High</p>
            <p className="text-white font-semibold">${range.max?.toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default PriceChart
