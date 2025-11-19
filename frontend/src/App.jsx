import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return
    const userMessage = { sender: 'user', text: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
    const response = await axios.post('http://localhost:8000/conversation', 
      {message: input
})

    const botText = response.data.message[0].text

    const botMessage = { sender: 'bot', text: botText }
    setMessages(prev => [...prev, botMessage])

  } catch (error) {
    console.error("Error:", error)
    const errorMessage = { sender: 'bot', text: "เกิดข้อผิดพลาด ไม่สามารถเชื่อมต่อ Server ได้" }
    setMessages(prev => [...prev, errorMessage])
  } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>AI Chatbot</h1>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <strong>{msg.sender === 'user' ? 'You' : 'AI'}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div className="message bot">... กำลังพิมพ์ ...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="พิมพ์ข้อความ..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>ส่ง</button>
      </div>
    </div>
  )
}

export default App