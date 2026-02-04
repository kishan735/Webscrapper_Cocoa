import React from 'react'
import { Brain, RefreshCw } from 'lucide-react'

function AnalysisCard({ analysis, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="skeleton h-6 w-40"></div>
          <div className="skeleton h-8 w-8 rounded"></div>
        </div>
        <div className="skeleton h-32 w-full"></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain size={20} className="text-violet-400" />
          <h3 className="font-semibold text-white">AI Market Analysis</h3>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700"
          >
            <RefreshCw size={18} />
          </button>
        )}
      </div>

      {analysis ? (
        <div className="prose prose-invert prose-sm max-w-none">
          <div className="text-slate-300 whitespace-pre-line leading-relaxed">
            {analysis}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Brain size={40} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No analysis available</p>
          <p className="text-slate-500 text-sm mt-1">
            Analysis will be generated when market data is available
          </p>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-slate-700">
        <p className="text-xs text-slate-500">
          AI-generated analysis based on current market data and news. Not financial advice.
        </p>
      </div>
    </div>
  )
}

export default AnalysisCard
