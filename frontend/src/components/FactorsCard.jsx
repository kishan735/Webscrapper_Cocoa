import React from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, CloudRain, Package, DollarSign, Building } from 'lucide-react'

const categoryIcons = {
  supply: Package,
  demand: TrendingUp,
  weather: CloudRain,
  market: DollarSign,
  geopolitical: Building,
  default: AlertTriangle,
}

function FactorsCard({ factors, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="skeleton h-6 w-32 mb-4"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="mb-3">
            <div className="skeleton h-16 w-full rounded-lg"></div>
          </div>
        ))}
      </div>
    )
  }

  const factorsList = factors?.factors || []

  if (factorsList.length === 0) {
    return (
      <div className="card">
        <h3 className="card-header">Key Market Factors</h3>
        <p className="text-slate-400">No factors data available</p>
      </div>
    )
  }

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'text-red-400 bg-red-500/20'
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20'
      default:
        return 'text-slate-400 bg-slate-500/20'
    }
  }

  const getDirectionIcon = (direction) => {
    return direction === 'bullish' ? (
      <TrendingUp size={16} className="text-green-400" />
    ) : (
      <TrendingDown size={16} className="text-red-400" />
    )
  }

  return (
    <div className="card">
      <h3 className="card-header">Key Market Factors</h3>

      <div className="space-y-3">
        {factorsList.map((factor, index) => {
          const Icon = categoryIcons[factor.category] || categoryIcons.default

          return (
            <div
              key={factor.id || index}
              className="p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-slate-600 rounded-lg">
                    <Icon size={20} className="text-violet-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{factor.name}</h4>
                    <p className="text-slate-400 text-sm mt-0.5">
                      {factor.description || `${factor.category} factor`}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1">
                  {getDirectionIcon(factor.direction)}
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getImpactColor(factor.impact)}`}>
                    {factor.impact} impact
                  </span>
                </div>
              </div>

              {factor.confidence && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Confidence</span>
                    <span className="text-slate-300">{(factor.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-violet-500"
                      style={{ width: `${factor.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default FactorsCard
