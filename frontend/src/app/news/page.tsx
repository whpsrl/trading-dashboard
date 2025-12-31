'use client'

import { useState, useEffect } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function NewsPage() {
  const [activeTab, setActiveTab] = useState<'generate' | 'articles'>('generate')
  
  // Generate tab state
  const [category, setCategory] = useState('crypto')
  const [aiProvider, setAiProvider] = useState('claude')
  const [style, setStyle] = useState('professional')
  const [language, setLanguage] = useState('en')
  const [keyword, setKeyword] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generatedArticle, setGeneratedArticle] = useState<any>(null)
  
  // Articles tab state
  const [articles, setArticles] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedArticle, setSelectedArticle] = useState<any>(null)
  const [publishing, setPublishing] = useState(false)

  const categories = [
    { value: 'crypto', label: '₿ Crypto', emoji: '₿' },
    { value: 'finance', label: '💰 Finance', emoji: '💰' },
    { value: 'tech', label: '💻 Tech', emoji: '💻' }
  ]

  const styles = [
    { value: 'professional', label: 'Professional' },
    { value: 'casual', label: 'Casual' },
    { value: 'technical', label: 'Technical' },
    { value: 'beginner', label: 'Beginner-Friendly' }
  ]

  const languages = [
    { value: 'en', label: '🇬🇧 English' },
    { value: 'it', label: '🇮🇹 Italiano' }
  ]

  const generateArticle = async () => {
    setGenerating(true)
    setGeneratedArticle(null)

    try {
      const params = new URLSearchParams({
        category,
        ai_provider: aiProvider,
        style,
        language,
        max_length: '500',
        save_to_db: 'true'
      })
      if (keyword) params.append('keyword', keyword)

      const response = await fetch(`${BACKEND_URL}/api/news/generate?${params.toString()}`, {
        method: 'POST'
      })

      if (!response.ok) {
        // Try to parse error message
        let errorMsg = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMsg = errorData.error || errorData.detail || errorMsg
        } catch {
          // Not JSON, might be HTML error page
          const text = await response.text()
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMsg = `Server error (${response.status}). Check backend logs.`
          } else {
            errorMsg = text.substring(0, 200)
          }
        }
        alert(`Error: ${errorMsg}`)
        return
      }

      const data = await response.json()
      
      if (data.success) {
        setGeneratedArticle(data)
        fetchArticles() // Refresh article list
      } else {
        alert(`Error: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error generating article:', error)
      alert('Failed to generate article')
    } finally {
      setGenerating(false)
    }
  }

  const fetchArticles = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${BACKEND_URL}/api/news/articles?limit=50`)
      const data = await response.json()
      if (data.success) {
        setArticles(data.articles)
      }
    } catch (error) {
      console.error('Error fetching articles:', error)
    } finally {
      setLoading(false)
    }
  }

  const publishArticle = async (articleId: number, topic: string = 'news_articles') => {
    if (!confirm('Publish this article to Telegram?')) return

    setPublishing(true)
    try {
      const response = await fetch(`${BACKEND_URL}/api/news/publish/${articleId}?topic=${topic}`, {
        method: 'POST'
      })

      if (!response.ok) {
        let errorMsg = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMsg = errorData.error || errorData.detail || errorMsg
        } catch {
          const text = await response.text()
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMsg = `Server error (${response.status}). Check backend logs.`
          } else {
            errorMsg = text.substring(0, 200)
          }
        }
        alert(`Error: ${errorMsg}`)
        return
      }
      
      const data = await response.json()
      
      if (data.success) {
        alert('✅ Article published to Telegram!')
        fetchArticles()
      } else {
        alert(`Error: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error publishing article:', error)
      alert('Failed to publish article')
    } finally {
      setPublishing(false)
    }
  }

  const deleteArticle = async (articleId: number) => {
    if (!confirm('Delete this article?')) return

    try {
      const response = await fetch(`${BACKEND_URL}/api/news/articles/${articleId}`, {
        method: 'DELETE'
      })
      const data = await response.json()
      
      if (data.success) {
        alert('✅ Article deleted')
        fetchArticles()
        if (selectedArticle?.id === articleId) {
          setSelectedArticle(null)
        }
      }
    } catch (error) {
      console.error('Error deleting article:', error)
      alert('Failed to delete article')
    }
  }

  useEffect(() => {
    if (activeTab === 'articles') {
      fetchArticles()
    }
  }, [activeTab])

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        📰 AI News & Articles
      </h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Generate AI-powered articles from financial news and publish to Telegram Topics
      </p>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '2px solid #e5e7eb' }}>
        <button
          onClick={() => setActiveTab('generate')}
          style={{
            padding: '1rem 2rem',
            background: activeTab === 'generate' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
            color: activeTab === 'generate' ? 'white' : '#666',
            border: 'none',
            borderBottom: activeTab === 'generate' ? '3px solid #667eea' : 'none',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '1rem',
            transition: 'all 0.2s'
          }}
        >
          ✨ Generate Article
        </button>
        <button
          onClick={() => setActiveTab('articles')}
          style={{
            padding: '1rem 2rem',
            background: activeTab === 'articles' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
            color: activeTab === 'articles' ? 'white' : '#666',
            border: 'none',
            borderBottom: activeTab === 'articles' ? '3px solid #667eea' : 'none',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '1rem',
            transition: 'all 0.2s'
          }}
        >
          📚 Saved Articles ({articles.length})
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          {/* Settings */}
          <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>⚙️ Settings</h2>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Category</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'column' }}>
                {categories.map(cat => (
                  <button
                    key={cat.value}
                    onClick={() => setCategory(cat.value)}
                    style={{
                      padding: '0.75rem',
                      background: category === cat.value ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f3f4f6',
                      color: category === cat.value ? 'white' : '#374151',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: category === cat.value ? 'bold' : 'normal',
                      transition: 'all 0.2s'
                    }}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>AI Provider</label>
              <select
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '1rem' }}
              >
                <option value="claude">🤖 Claude Sonnet 4</option>
                <option value="groq">⚡ Groq (Llama 3.3)</option>
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '1rem' }}
              >
                {styles.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '1rem' }}
              >
                {languages.map(lang => (
                  <option key={lang.value} value={lang.value}>{lang.label}</option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Keyword (Optional)</label>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="e.g., Bitcoin, Fed, AI..."
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '1rem' }}
              />
            </div>

            <button
              onClick={generateArticle}
              disabled={generating}
              style={{
                width: '100%',
                padding: '1rem',
                background: generating ? '#9ca3af' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: generating ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '1.1rem',
                transition: 'all 0.2s'
              }}
            >
              {generating ? '✨ Generating...' : '🚀 Generate Article'}
            </button>
          </div>

          {/* Preview */}
          <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', minHeight: '600px' }}>
            {generating ? (
              <div style={{ textAlign: 'center', padding: '4rem' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✨</div>
                <p style={{ color: '#666', fontSize: '1.1rem' }}>Generating article with AI...</p>
                <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginTop: '0.5rem' }}>This may take 10-20 seconds</p>
              </div>
            ) : generatedArticle ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e5e7eb' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>📄 Generated Article</h2>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{ padding: '0.5rem 1rem', background: '#f3f4f6', borderRadius: '8px', fontSize: '0.9rem', color: '#666' }}>
                      {generatedArticle.article.word_count} words
                    </span>
                    <span style={{ padding: '0.5rem 1rem', background: '#f3f4f6', borderRadius: '8px', fontSize: '0.9rem', color: '#666' }}>
                      {generatedArticle.source_count} sources
                    </span>
                  </div>
                </div>
                
                <div style={{ background: '#f9fafb', padding: '1.5rem', borderRadius: '12px', marginBottom: '1.5rem', maxHeight: '500px', overflowY: 'auto' }}>
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#374151' }}>
                    {generatedArticle.article.content}
                  </div>
                </div>

                {generatedArticle.article_id && (
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                      onClick={() => publishArticle(generatedArticle.article_id, 'news_articles')}
                      style={{
                        flex: 1,
                        padding: '1rem',
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        transition: 'all 0.2s'
                      }}
                    >
                      📱 Publish to Telegram
                    </button>
                    <button
                      onClick={() => {
                        setGeneratedArticle(null)
                        fetchArticles()
                      }}
                      style={{
                        padding: '1rem 1.5rem',
                        background: '#f3f4f6',
                        color: '#374151',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                      }}
                    >
                      ✨ New Article
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '4rem', color: '#9ca3af' }}>
                <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📰</div>
                <p style={{ fontSize: '1.1rem' }}>Configure settings and generate an article</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Articles Tab */}
      {activeTab === 'articles' && (
        <div style={{ display: 'grid', gridTemplateColumns: selectedArticle ? '1fr 2fr' : '1fr', gap: '2rem' }}>
          {/* Articles List */}
          <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>📚 Saved Articles</h2>
              <button
                onClick={fetchArticles}
                style={{ padding: '0.5rem 1rem', background: '#f3f4f6', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
              >
                🔄 Refresh
              </button>
            </div>

            {loading ? (
              <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>Loading...</p>
            ) : articles.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#9ca3af', padding: '2rem' }}>No articles yet. Generate your first one!</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '700px', overflowY: 'auto' }}>
                {articles.map((article) => (
                  <div
                    key={article.id}
                    onClick={() => setSelectedArticle(article)}
                    style={{
                      padding: '1rem',
                      background: selectedArticle?.id === article.id ? '#f0f9ff' : '#f9fafb',
                      border: selectedArticle?.id === article.id ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', margin: 0, flex: 1 }}>
                        {article.title}
                      </h3>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        background: article.status === 'published' ? '#10b981' : article.status === 'draft' ? '#f59e0b' : '#6b7280',
                        color: 'white',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        marginLeft: '0.5rem'
                      }}>
                        {article.status}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', fontSize: '0.85rem', color: '#6b7280' }}>
                      <span>{article.category}</span>
                      <span>•</span>
                      <span>{article.language}</span>
                      <span>•</span>
                      <span>{article.word_count} words</span>
                      <span>•</span>
                      <span>{new Date(article.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Article Preview */}
          {selectedArticle && (
            <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e5e7eb' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{selectedArticle.title}</h2>
                <button
                  onClick={() => setSelectedArticle(null)}
                  style={{ padding: '0.5rem 1rem', background: '#f3f4f6', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <div style={{ background: '#f9fafb', padding: '1.5rem', borderRadius: '12px', marginBottom: '1.5rem', maxHeight: '500px', overflowY: 'auto' }}>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#374151' }}>
                  {selectedArticle.content}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                {selectedArticle.status !== 'published' && (
                  <button
                    onClick={() => publishArticle(selectedArticle.id)}
                    disabled={publishing}
                    style={{
                      flex: 1,
                      padding: '1rem',
                      background: publishing ? '#9ca3af' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: publishing ? 'not-allowed' : 'pointer',
                      fontWeight: 'bold',
                      transition: 'all 0.2s'
                    }}
                  >
                    {publishing ? 'Publishing...' : '📱 Publish to Telegram'}
                  </button>
                )}
                <button
                  onClick={() => deleteArticle(selectedArticle.id)}
                  style={{
                    padding: '1rem 1.5rem',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

