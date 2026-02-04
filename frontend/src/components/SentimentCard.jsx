import React from 'react'
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react'

function SentimentCard({ marketData, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="skeleton h-6 w-32 mb-4"></div>
        <div className="skeleton h-16 w-full"></div>
      </div>
    )
  }

  if (!marketData) {
    return null
  }

  const { sentiment, confidence, bullish_signals, bearish_signals } = marketData

  const sentimentConfig = {
    bullish: {
      icon: TrendingUp,
      color: 'text-green-400',
      bg: 'bg-green-500/20',
      label: 'Bullish',
    },
    bearish: {
      icon: TrendingDown,
      color: 'text-red-400',
      bg: 'bg-red-500/20',
      label: 'Bearish',
    },
    neutral: {
      icon: Minus,
      color: 'text-slate-400',
      bg: 'bg-slate-500/20',
      label: 'Neutral',
    },
  }

  const config = sentimentConfig[sentiment] || sentimentConfig.neutral
  const SentimentIcon = config.icon

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-4">
        <Activity size={20} className="text-violet-400" />
        <h3 className="font-semibold text-white">Market Sentiment</h3>
      </div>

      {/* Main sentiment indicator */}
      <div className={`flex items-center justify-center p-4 rounded-xl ${config.bg} mb-4`}>
        <SentimentIcon size={32} className={config.color} />
        <span className={`text-2xl font-bold ml-3 ${config.color}`}>
          {config.label}
        </span>
      </div>

      {/* Confidence meter */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-slate-400">Confidence</span>
          <span className="text-white">{(confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-violet-500 transition-all duration-500"
            style={{ width: `${confidence * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Signal counts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-green-500/10 rounded-lg">
          <p className="text-2xl font-bold text-green-400">{bullish_signals}</p>
          <p className="text-xs text-slate-400">Bullish Signals</p>
        </div>
        <div className="text-center p-3 bg-red-500/10 rounded-lg">
          <p className="text-2xl font-bold text-red-400">{bearish_signals}</p>
          <p className="text-xs text-slate-400">Bearish Signals</p>
        </div>
      </div>
    </div>
  )
}

export default SentimentCard
