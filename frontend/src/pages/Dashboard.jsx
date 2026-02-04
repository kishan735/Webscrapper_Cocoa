import React, { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import { usePollingApi } from '../hooks/useApi'
import PriceCard from '../components/PriceCard'
import SentimentCard from '../components/SentimentCard'
import PriceChart from '../components/PriceChart'
import NewsCard from '../components/NewsCard'
import FactorsCard from '../components/FactorsCard'
import AnalysisCard from '../components/AnalysisCard'

function Dashboard() {
  const [chartPeriod, setChartPeriod] = useState('30d')
  const [chartData, setChartData] = useState(null)
  const [chartLoading, setChartLoading] = useState(true)

  // Fetch dashboard summary with polling (every 60 seconds)
  const {
    data: summaryData,
    loading: summaryLoading,
    refetch: refetchSummary
  } = usePollingApi(() => api.getDashboardSummary(), 60000)

  // Fetch news feed
  const {
    data: newsData,
    loading: newsLoading
  } = usePollingApi(() => api.getNewsFeed(5), 120000)

  // Fetch key factors
  const {
    data: factorsData,
    loading: factorsLoading
  } = usePollingApi(() => api.getKeyFactors(), 300000)

  // Fetch analysis
  const {
    data: analysisData,
    loading: analysisLoading,
    refetch: refetchAnalysis
  } = usePollingApi(() => api.getQuickAnalysis(), 300000)

  // Fetch chart data
  const fetchChartData = useCallback(async (period) => {
    setChartLoading(true)
    try {
      const data = await api.getPriceChart(period)
      setChartData(data)
    } catch (error) {
      console.error('Failed to fetch chart data:', error)
    } finally {
      setChartLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchChartData(chartPeriod)
  }, [chartPeriod, fetchChartData])

  const handlePeriodChange = (period) => {
    setChartPeriod(period)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Cocoa Market Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Real-time price tracking and market analysis
          </p>
        </div>
        {summaryData?.timestamp && (
          <p className="text-sm text-slate-500">
            Last updated: {new Date(summaryData.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Top Row - Price and Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PriceCard
            priceData={summaryData?.price}
            loading={summaryLoading}
            onRefresh={refetchSummary}
          />
        </div>
        <div>
          <SentimentCard
            marketData={summaryData?.market}
            loading={summaryLoading}
          />
        </div>
      </div>

      {/* Price Chart */}
      <PriceChart
        chartData={chartData}
        loading={chartLoading}
        period={chartPeriod}
        onPeriodChange={handlePeriodChange}
      />

      {/* Bottom Row - News, Factors, Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <NewsCard
            articles={newsData?.articles}
            loading={newsLoading}
            limit={5}
          />
        </div>
        <div className="space-y-6">
          <FactorsCard
            factors={factorsData}
            loading={factorsLoading}
          />
        </div>
      </div>

      {/* AI Analysis */}
      <AnalysisCard
        analysis={analysisData?.analysis}
        loading={analysisLoading}
        onRefresh={refetchAnalysis}
      />

      {/* Quick Stats */}
      {summaryData?.stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <p className="text-slate-400 text-sm">News This Week</p>
            <p className="text-2xl font-bold text-white mt-1">
              {summaryData.stats.news_this_week}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-slate-400 text-sm">Data Freshness</p>
            <p className="text-sm font-medium text-green-400 mt-2">
              {summaryData.stats.data_freshness ? 'Live' : 'Stale'}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-slate-400 text-sm">Market Status</p>
            <p className="text-sm font-medium text-violet-400 mt-2">
              {summaryData.market?.sentiment?.toUpperCase() || 'N/A'}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-slate-400 text-sm">Confidence</p>
            <p className="text-2xl font-bold text-white mt-1">
              {((summaryData.market?.confidence || 0) * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
