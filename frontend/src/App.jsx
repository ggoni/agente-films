import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [currentAgent, setCurrentAgent] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Check API health
    axios.get(`${API_URL}/health`)
      .then(res => setHealth(res.data))
      .catch(err => console.error('Health check failed:', err))
      .finally(() => setLoading(false))
  }, [])

  const createSession = async () => {
    try {
      const response = await axios.post(`${API_URL}/sessions`)
      setSessionId(response.data.id)
      setMessages([{
        role: 'system',
        content: '✨ Session created! Ask me to create a film concept, develop characters, or write a screenplay.'
      }])
    } catch (error) {
      console.error('Failed to create session:', error)
      alert('Failed to create session. Check console for details.')
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || sending) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setSending(true)
    setCurrentAgent('Processing...')

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      // Simulate agent progress updates
      const agentSteps = ['Greeter', 'Researcher', 'Screenwriter', 'Critic']
      let stepIndex = 0

      const progressInterval = setInterval(() => {
        if (stepIndex < agentSteps.length) {
          setCurrentAgent(`${agentSteps[stepIndex]} thinking...`)
          stepIndex++
        }
      }, 2000)

      const response = await axios.post(
        `${API_URL}/sessions/${sessionId}/messages`,
        { message: userMessage }
      )

      clearInterval(progressInterval)

      // Add agent response to chat
      setMessages(prev => [...prev, {
        role: 'agent',
        content: response.data.response,
        thoughts: response.data.thoughts || []
      }])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, {
        role: 'error',
        content: '❌ Failed to send message. Please try again.'
      }])
    } finally {
      setSending(false)
      setCurrentAgent('')
    }
  }

  if (loading) {
    return <div className="app">Loading...</div>
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎬 Agente Films</h1>
        <p>Multi-Agent Filmmaking System</p>
        {health && (
          <div className="header-status">
            <span className="status-indicator">●</span> Connected
          </div>
        )}
      </header>

      <main className="main-chat">
        {!sessionId ? (
          <div className="welcome">
            <div className="welcome-card">
              <h2>Welcome to Agente Films</h2>
              <p>Start a conversation with our AI filmmaking agents</p>
              <button onClick={createSession} className="btn-primary">
                🎬 Start New Session
              </button>

              <div className="features">
                <div className="feature">
                  <span>💡</span>
                  <div>
                    <strong>Create Concepts</strong>
                    <p>Generate unique film ideas</p>
                  </div>
                </div>
                <div className="feature">
                  <span>✍️</span>
                  <div>
                    <strong>Write Scripts</strong>
                    <p>Develop screenplays and dialogue</p>
                  </div>
                </div>
                <div className="feature">
                  <span>👥</span>
                  <div>
                    <strong>Build Characters</strong>
                    <p>Create compelling character profiles</p>
                  </div>
                </div>
              </div>

              <div className="quick-links">
                <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer">
                  📚 API Docs
                </a>
                <a href="http://localhost:4000/" target="_blank" rel="noopener noreferrer">
                  🤖 LiteLLM
                </a>
              </div>
            </div>
          </div>
        ) : (
          <div className="chat-container">
            <div className="chat-header">
              <div className="session-info">
                <span className="session-label">Session:</span>
                <code className="session-id">{sessionId.split('-')[0]}...</code>
              </div>
              <button
                onClick={() => {
                  setSessionId(null)
                  setMessages([])
                }}
                className="btn-secondary"
              >
                New Session
              </button>
            </div>

            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message message-${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : msg.role === 'agent' ? '🎬' : 'ℹ️'}
                  </div>
                  <div className="message-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                    {msg.thoughts && msg.thoughts.length > 0 && (
                      <div className="thoughts-container">
                        <div className="thoughts-header">🧠 Chain of Thought</div>
                        {msg.thoughts.map((thought, tIdx) => (
                          <div key={tIdx} className="thought-item">
                            <span className="thought-agent">{thought.agent}</span>
                            <span className="thought-text">{thought.text}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {sending && (
                <div className="message message-agent">
                  <div className="message-avatar">🎬</div>
                  <div className="message-content typing">
                    <div className="typing-text">{currentAgent}</div>
                    <div className="typing-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={sendMessage} className="input-form">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me to create a film concept..."
                disabled={sending}
                className="message-input"
              />
              <button
                type="submit"
                disabled={sending || !inputMessage.trim()}
                className="btn-send"
              >
                {sending ? '...' : '→'}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
