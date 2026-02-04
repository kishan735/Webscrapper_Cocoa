const API_BASE = '/api'

class ApiService {
  async fetch(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Dashboard endpoints
  async getDashboardSummary() {
    return this.fetch('/dashboard/summary')
  }

  async getPriceChart(period = '30d') {
    return this.fetch(`/dashboard/price-chart?period=${period}`)
  }

  async getNewsFeed(limit = 10) {
    return this.fetch(`/dashboard/news-feed?limit=${limit}`)
  }

  async getKeyFactors() {
    return this.fetch('/dashboard/key-factors')
  }

  async getQuickAnalysis() {
    return this.fetch('/dashboard/quick-analysis')
  }

  // API v1 endpoints
  async getCurrentPrice() {
    return this.fetch('/v1/price/current')
  }

  async getPriceHistory(days = 30) {
    return this.fetch(`/v1/price/history?days=${days}`)
  }

  async getPriceStats() {
    return this.fetch('/v1/price/stats')
  }

  async getNews(limit = 20, category = null) {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (category) params.append('category', category)
    return this.fetch(`/v1/news?${params}`)
  }

  async getNewsArticle(id) {
    return this.fetch(`/v1/news/${id}`)
  }

  async getMarketFactors() {
    return this.fetch('/v1/factors')
  }

  async getMarketOverview() {
    return this.fetch('/v1/analysis/overview')
  }

  async getMarketOutlook() {
    return this.fetch('/v1/analysis/outlook')
  }

  async getDailyDigest() {
    return this.fetch('/v1/analysis/digest')
  }

  async triggerScrape() {
    return this.fetch('/v1/scrape/trigger', { method: 'POST' })
  }
}

export const api = new ApiService()
export default api
