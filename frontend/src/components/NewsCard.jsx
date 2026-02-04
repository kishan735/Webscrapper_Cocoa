import React from 'react'
import { ExternalLink, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

function NewsCard({ articles, loading, limit = 5 }) {
  if (loading) {
    return (
      <div className="card">
        <div className="skeleton h-6 w-32 mb-4"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="mb-4 pb-4 border-b border-slate-700 last:border-0">
            <div className="skeleton h-5 w-full mb-2"></div>
            <div className="skeleton h-4 w-3/4"></div>
          </div>
        ))}
      </div>
    )
  }

  const displayArticles = articles?.slice(0, limit) || []

  if (displayArticles.length === 0) {
    return (
      <div className="card">
        <h3 className="card-header">Latest News</h3>
        <p className="text-slate-400">No news articles available</p>
      </div>
    )
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <TrendingUp size={14} className="text-green-400" />
      case 'negative':
        return <TrendingDown size={14} className="text-red-400" />
      default:
        return <Minus size={14} className="text-slate-400" />
    }
  }

  const getSentimentBadge = (sentiment) => {
    const badges = {
      positive: 'badge-bullish',
      negative: 'badge-bearish',
      neutral: 'badge-neutral',
    }
    return badges[sentiment] || badges.neutral
  }

  return (
    <div className="card">
      <h3 className="card-header flex items-center justify-between">
        <span>Latest News</span>
        <span className="text-xs font-normal text-slate-400">
          {displayArticles.length} articles
        </span>
      </h3>

      <div className="space-y-4">
        {displayArticles.map((article, index) => (
          <article
            key={article.id || index}
            className="pb-4 border-b border-slate-700 last:border-0 last:pb-0"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group"
                >
                  <h4 className="text-white font-medium group-hover:text-violet-400 transition-colors line-clamp-2">
                    {article.title}
                  </h4>
                </a>

                {article.summary && (
                  <p className="text-slate-400 text-sm mt-1 line-clamp-2">
                    {article.summary}
                  </p>
                )}

                <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    {getSentimentIcon(article.sentiment)}
                    <span className={`badge ${getSentimentBadge(article.sentiment)}`}>
                      {article.sentiment || 'neutral'}
                    </span>
                  </span>

                  <span className="text-slate-600">|</span>

                  <span>{article.source}</span>

                  {article.published_at && (
                    <>
                      <span className="text-slate-600">|</span>
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        {formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}
                      </span>
                    </>
                  )}
                </div>

                {article.categories && article.categories.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {article.categories.slice(0, 3).map((category, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-slate-400 hover:text-violet-400 transition-colors"
              >
                <ExternalLink size={16} />
              </a>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}

export default NewsCard
