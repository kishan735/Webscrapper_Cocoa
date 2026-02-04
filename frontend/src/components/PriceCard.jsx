import React from 'react'
import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react'

function PriceCard({ priceData, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="card">
        <div className="skeleton h-8 w-32 mb-2"></div>
        <div className="skeleton h-12 w-48 mb-4"></div>
        <div className="skeleton h-6 w-24"></div>
      </div>
    )
  }

  if (!priceData) {
    return (
      <div className="card">
        <p className="text-slate-400">Unable to load price data</p>
      </div>
    )
  }

  const { current, formatted, change_24h, change_percent_24h, high_52_week, low_52_week } = priceData

  const isPositive = change_24h > 0
  const isNegative = change_24h < 0
  const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus
  const trendColor = isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-slate-400'

  return (
    <div className="card relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-500/10 to-transparent rounded-full -mr-16 -mt-16"></div>

      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-slate-400 text-sm mb-1">Cocoa Price (ICE Futures)</p>
          <h2 className="text-4xl font-bold text-white">{formatted}</h2>
          <p className="text-slate-500 text-sm mt-1">USD per metric ton</p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700"
          >
            <RefreshCw size={20} />
          </button>
        )}
      </div>

      {/* Price change */}
      <div className={`flex items-center space-x-2 ${trendColor}`}>
        <TrendIcon size={20} />
        <span className="text-lg font-semibold">
          {isPositive ? '+' : ''}{change_24h?.toFixed(2) || '0.00'}
        </span>
        <span className="text-sm">
          ({isPositive ? '+' : ''}{change_percent_24h?.toFixed(2) || '0.00'}%)
        </span>
        <span className="text-slate-500 text-sm">24h</span>
      </div>

      {/* 52-week range */}
      {high_52_week && low_52_week && (
        <div className="mt-6 pt-4 border-t border-slate-700">
          <p className="text-slate-400 text-sm mb-2">52-Week Range</p>
          <div className="flex justify-between text-sm">
            <span className="text-red-400">${low_52_week.toLocaleString()}</span>
            <span className="text-slate-500">|</span>
            <span className="text-green-400">${high_52_week.toLocaleString()}</span>
          </div>
          {/* Range indicator */}
          <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
              style={{
                width: `${((current - low_52_week) / (high_52_week - low_52_week)) * 100}%`
              }}
            ></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PriceCard
