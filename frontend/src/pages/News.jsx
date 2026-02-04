import React, { useState } from 'react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { Search, Filter, RefreshCw, ExternalLink, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'price', label: 'Price' },
  { value: 'supply', label: 'Supply' },
  { value: 'demand', label: 'Demand' },
  { value: 'weather', label: 'Weather' },
  { value: 'market', label: 'Market' },
  { value: 'geopolitical', label: 'Geopolitical' },
]

function News() {
  const [selectedCategory, setSelectedCategory] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const { data, loading, error, refetch } = useApi(
    () => api.getNews(50, selectedCategory || null),
    [selectedCategory]
  )

  const articles = data || []

  // Filter by search query
  const filteredArticles = articles.filter(article => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      article.title?.toLowerCase().includes(query) ||
      article.summary?.toLowerCase().includes(query) ||
      article.source?.toLowerCase().includes(query)
    )
  })

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <TrendingUp size={16} className="text-green-400" />
      case 'negative':
        return <TrendingDown size={16} className="text-red-400" />
      default:
        return <Minus size={16} className="text-slate-400" />
    }
  }

  const getSentimentClass = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'negative':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Cocoa Market News</h1>
          <p className="text-slate-400 mt-1">
            Latest news and developments affecting cocoa prices
          </p>
        </div>
        <button
          onClick={refetch}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg transition-colors"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search news..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
            />
          </div>

          {/* Category filter */}
          <div className="relative">
            <Filter size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white appearance-none cursor-pointer focus:outline-none focus:border-violet-500"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center justify-between">
        <p className="text-slate-400 text-sm">
          Showing {filteredArticles.length} articles
        </p>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card">
              <div className="skeleton h-6 w-3/4 mb-3"></div>
              <div className="skeleton h-4 w-full mb-2"></div>
              <div className="skeleton h-4 w-2/3"></div>
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="card bg-red-500/10 border-red-500/30">
          <p className="text-red-400">Failed to load news: {error}</p>
        </div>
      )}

      {/* News list */}
      {!loading && !error && (
        <div className="space-y-4">
          {filteredArticles.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-slate-400">No news articles found</p>
            </div>
          ) : (
            filteredArticles.map((article, index) => (
              <article
                key={article.id || index}
                className="card hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getSentimentIcon(article.sentiment)}
                      <span className={`px-2 py-0.5 text-xs font-medium rounded border ${getSentimentClass(article.sentiment)}`}>
                        {article.sentiment || 'neutral'}
                      </span>
                      {article.importance_score >= 0.7 && (
                        <span className="px-2 py-0.5 text-xs font-medium rounded bg-violet-500/20 text-violet-400 border border-violet-500/30">
                          High Impact
                        </span>
                      )}
                    </div>

                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group"
                    >
                      <h2 className="text-lg font-semibold text-white group-hover:text-violet-400 transition-colors">
                        {article.title}
                      </h2>
                    </a>

                    {article.summary && (
                      <p className="text-slate-400 mt-2 line-clamp-3">
                        {article.summary}
                      </p>
                    )}

                    <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-slate-500">
                      <span className="font-medium text-slate-400">{article.source}</span>

                      {article.published_at && (
                        <span className="flex items-center gap-1">
                          <Clock size={14} />
                          {formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}
                        </span>
                      )}

                      {article.categories && (
                        <div className="flex gap-1">
                          {(Array.isArray(article.categories) ? article.categories : article.categories.split(',')).slice(0, 3).map((cat, i) => (
                            <span key={i} className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded">
                              {cat.trim()}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-3 text-slate-400 hover:text-violet-400 hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    <ExternalLink size={20} />
                  </a>
                </div>
              </article>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default News
