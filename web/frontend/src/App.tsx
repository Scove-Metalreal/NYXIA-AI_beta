import { useState, useEffect, useRef } from 'react'

function App() {
  const wsRef = useRef<WebSocket | null>(null)
  const [message, setMessage] = useState<string>('')
  const [messages, setMessages] = useState<string[]>([])
  const wsUrl = 'ws://127.0.0.1:8000/ws'
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const newWs = new WebSocket(wsUrl)

    newWs.onopen = () => {
      console.log('WebSocket Connected')
      setMessages((prev) => [...prev, 'System: WebSocket Connected'])
    }

    newWs.onmessage = (event) => {
      setMessages((prev) => [...prev, `Misa: ${event.data}`])
    }

    newWs.onclose = () => {
      console.log('WebSocket Disconnected')
      setMessages((prev) => [...prev, 'System: WebSocket Disconnected'])
      wsRef.current = null // Clear WebSocket object on close
    }

    newWs.onerror = (error) => {
      console.error('WebSocket Error:', error)
      setMessages((prev) => [...prev, `System: WebSocket Error: ${error.type}`])
    }

    wsRef.current = newWs

    return () => {
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close()
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && message.trim() !== '') {
      wsRef.current.send(message)
      setMessages((prev) => [...prev, `You: ${message}`])
      setMessage('')
    }
  }

  return (
    <div className="app-container">
      <div className="avatar-section">
        <h2>Misa Avatar</h2>
        {/* Placeholder for VTuber model */}
      </div>
      <div className="chatbox-section">
        <h2>Chat Box</h2>
        <div style={{ flex: 1, overflowY: 'auto', padding: '10px', border: '1px solid #ccc', marginBottom: '10px' }}>
          {messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault() // Prevent default behavior (e.g., new line in textarea)
              sendMessage()
            }
          }}
          placeholder="Type your message..."
          style={{ width: 'calc(100% - 22px)', padding: '10px', border: '1px solid #ccc' }}
        />
        <button onClick={sendMessage} style={{ width: '100%', padding: '10px', marginTop: '10px' }}>Send</button>
      </div>
      <div className="controller-section">
        <h2>Controller</h2>
        {/* Placeholder for controls */}
      </div>
    </div>
  )
}

export default App
