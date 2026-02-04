import React from 'react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import {
  Brain,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Target,
  Eye,
  RefreshCw,
  CheckCircle,
  XCircle
} from 'lucide-react'

function Analysis() {
  const {
    data: overviewData,
    loading: overviewLoading,
    refetch: refetchOverview
  } = useApi(() => api.getMarketOverview())

  const {
    data: outlookData,
    loading: outlookLoading,
    refetch: refetchOutlook
  } = useApi(() => api.getMarketOutlook())

  const {
    data: digestData,
    loading: digestLoading,
    refetch: refetchDigest
  } = useApi(() => api.getDailyDigest())

  const handleRefreshAll = () => {
    refetchOverview()
    refetchOutlook()
    refetchDigest()
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return 'text-green-400'
      case 'bearish':
        return 'text-red-400'
      default:
        return 'text-slate-400'
    }
  }

  const getSentimentBg = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return 'bg-green-500/20'
      case 'bearish':
        return 'bg-red-500/20'
      default:
        return 'bg-slate-500/20'
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Market Analysis</h1>
          <p className="text-slate-400 mt-1">
            AI-powered insights and market outlook
          </p>
        </div>
        <button
          onClick={handleRefreshAll}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg transition-colors"
        >
          <RefreshCw size={18} />
          Refresh All
        </button>
      </div>

      {/* Price Summary */}
      {overviewData && (
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-violet-500/20 rounded-lg">
              <TrendingUp size={24} className="text-violet-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                ${overviewData.current_price?.toLocaleString()}
              </h2>
              <p className="text-slate-400 text-sm">Current Cocoa Price (USD/MT)</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: '24h', value: overviewData.price_changes?.['24h'], suffix: '%' },
              { label: '7d', value: overviewData.price_changes?.['7d'], suffix: '%' },
              { label: '30d', value: overviewData.price_changes?.['30d'], suffix: '%' },
              { label: '52W High', value: overviewData.price_changes?.high_52, prefix: '$' },
              { label: '52W Low', value: overviewData.price_changes?.low_52, prefix: '$' },
            ].map((item, i) => (
              <div key={i} className="text-center p-3 bg-slate-700/50 rounded-lg">
                <p className="text-slate-400 text-xs">{item.label}</p>
                <p className={`text-lg font-semibold ${
                  typeof item.value === 'number' && item.suffix === '%'
                    ? item.value >= 0 ? 'text-green-400' : 'text-red-400'
                    : 'text-white'
                }`}>
                  {item.prefix}{typeof item.value === 'number' ? item.value.toLocaleString() : 'N/A'}{item.suffix && typeof item.value === 'number' ? item.suffix : ''}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Market Overview */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Brain size={20} className="text-violet-400" />
            <h3 className="font-semibold text-white">Market Overview</h3>
          </div>
          {overviewData?.overview?.sentiment && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentBg(overviewData.overview.sentiment)} ${getSentimentColor(overviewData.overview.sentiment)}`}>
              {overviewData.overview.sentiment.toUpperCase()}
            </span>
          )}
        </div>

        {overviewLoading ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-full"></div>
            <div className="skeleton h-4 w-3/4"></div>
          </div>
        ) : overviewData?.overview ? (
          <div className="space-y-4">
            <p className="text-slate-300 leading-relaxed">
              {overviewData.overview.market_summary}
            </p>

            {overviewData.overview.key_events?.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-400 mb-2">Key Events</h4>
                <ul className="space-y-2">
                  {overviewData.overview.key_events.map((event, i) => (
                    <li key={i} className="flex items-start gap-2 text-slate-300">
                      <CheckCircle size={16} className="text-violet-400 mt-0.5 flex-shrink-0" />
                      <span>{event}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {overviewData.overview.price_drivers?.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-400 mb-2">Price Drivers</h4>
                <div className="flex flex-wrap gap-2">
                  {overviewData.overview.price_drivers.map((driver, i) => (
                    <span key={i} className="px-3 py-1 bg-slate-700 text-slate-300 rounded-full text-sm">
                      {driver}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-slate-400">No overview data available</p>
        )}
      </div>

      {/* Market Outlook */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Eye size={20} className="text-violet-400" />
          <h3 className="font-semibold text-white">Market Outlook</h3>
        </div>

        {outlookLoading ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-full"></div>
            <div className="skeleton h-4 w-3/4"></div>
          </div>
        ) : outlookData?.outlook ? (
          <div className="space-y-6">
            <p className="text-slate-300 leading-relaxed">
              {outlookData.outlook.outlook_summary}
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Bias indicators */}
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <span className="text-slate-400">Short-term Bias</span>
                  <span className={`font-medium ${getSentimentColor(outlookData.outlook.short_term_bias)}`}>
                    {outlookData.outlook.short_term_bias?.toUpperCase() || 'N/A'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <span className="text-slate-400">Medium-term Bias</span>
                  <span className={`font-medium ${getSentimentColor(outlookData.outlook.medium_term_bias)}`}>
                    {outlookData.outlook.medium_term_bias?.toUpperCase() || 'N/A'}
                  </span>
                </div>
              </div>

              {/* Confidence from sentiment */}
              {outlookData.sentiment && (
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <h4 className="text-sm font-medium text-slate-400 mb-3">Sentiment Analysis</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Confidence</span>
                      <span className="text-white">{(outlookData.sentiment.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-violet-500"
                        style={{ width: `${outlookData.sentiment.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Trends, Risks, Opportunities */}
            <div className="grid md:grid-cols-3 gap-4">
              {outlookData.outlook.trends_to_watch?.length > 0 && (
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Target size={18} className="text-blue-400" />
                    <h4 className="font-medium text-white">Trends to Watch</h4>
                  </div>
                  <ul className="space-y-2">
                    {outlookData.outlook.trends_to_watch.map((trend, i) => (
                      <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        {trend}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {outlookData.outlook.risk_factors?.length > 0 && (
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle size={18} className="text-red-400" />
                    <h4 className="font-medium text-white">Risk Factors</h4>
                  </div>
                  <ul className="space-y-2">
                    {outlookData.outlook.risk_factors.map((risk, i) => (
                      <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="text-red-400">•</span>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {outlookData.outlook.opportunities?.length > 0 && (
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={18} className="text-green-400" />
                    <h4 className="font-medium text-white">Opportunities</h4>
                  </div>
                  <ul className="space-y-2">
                    {outlookData.outlook.opportunities.map((opp, i) => (
                      <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="text-green-400">•</span>
                        {opp}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-slate-400">No outlook data available</p>
        )}
      </div>

      {/* Daily Digest */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Brain size={20} className="text-violet-400" />
          <h3 className="font-semibold text-white">Daily Market Digest</h3>
        </div>

        {digestLoading ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-full"></div>
            <div className="skeleton h-4 w-full"></div>
            <div className="skeleton h-4 w-3/4"></div>
          </div>
        ) : digestData?.digest ? (
          <div className="prose prose-invert prose-sm max-w-none">
            <div className="text-slate-300 whitespace-pre-line leading-relaxed">
              {digestData.digest}
            </div>
          </div>
        ) : (
          <p className="text-slate-400">No digest available</p>
        )}

        <div className="mt-4 pt-4 border-t border-slate-700">
          <p className="text-xs text-slate-500">
            AI-generated analysis based on current market data and news. This is not financial advice.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Analysis
