import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [chatMode, setChatMode] = useState('general')
  
  const [selectedFile, setSelectedFile] = useState(null)
  const [currentUploadedFile, setCurrentUploadedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  
  const [processStatus, setProcessStatus] = useState('') 
  
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
        setSelectedFile(e.target.files[0])
    }
  }

  const handleReset = () => {
    if (window.confirm("ต้องการล้างบทสนทนาทั้งหมดหรือไม่?")) {
      setMessages([])
      setInput('')
      setProcessStatus('')
    }
  }

  const checkEmbeddingStatus = async (filename) => {
    try {
     
      await new Promise(resolve => setTimeout(resolve, 5000));

      const res = await axios.post('http://localhost:8000/status');
      const status = res.data.message;

      console.log("Polling Status:", status);

      if (status === 'processing') {
      
        setProcessStatus(`⏳ กำลังประมวลผลข้อมูล... (Status: ${status})`);
        
        await checkEmbeddingStatus(filename);

      } else if (status === 'done') {

        await axios.get('http://localhost:8000/reset_status');

        setProcessStatus('');
        
        setMessages(prev => [...prev, { 
            sender: 'bot', 
            text: `✅ ประมวลผลไฟล์ "${filename}" เสร็จสมบูรณ์!` 
        }]);

        setCurrentUploadedFile(filename);
        setSelectedFile(null);
        setUploading(false); 

      } else {
        setUploading(false);
        setProcessStatus('');
      }

    } catch (error) {
      console.error("Status check error:", error);
      setProcessStatus(`❌ เกิดข้อผิดพลาดในการเช็คสถานะ`);
      setUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("กรุณาเลือกไฟล์ PDF ก่อน")
    setUploading(true) 
    setProcessStatus(`⏳ กำลังอัปโหลดไฟล์: "${selectedFile.name}"...`)
    
    const formData = new FormData()
    formData.append('file', selectedFile)
    
    try {
      await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setProcessStatus(`⏳ อัปโหลดเสร็จแล้ว กำลังเริ่มประมวลผล...`)
      checkEmbeddingStatus(selectedFile.name);

    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { sender: 'bot', text: `❌ อัปโหลดล้มเหลว: ${error.message}` }])
      setUploading(false)
      setProcessStatus('')
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return
    if (loading) return

    const userMessage = { sender: 'user', text: input }
    setMessages(prev => [...prev, userMessage])
    
    setInput('') 
    setLoading(true)

    const historyPayload = messages.map(m => ({
        sender: m.sender,
        text: m.text
    }))

    try {
      const response = await axios.post('http://localhost:8000/conversation', {
        message: input,
        mode: chatMode,
        history: historyPayload 
      })

      const rawData = response.data.message
      let botText = ""

      if (typeof rawData === 'string') botText = rawData
      else if (Array.isArray(rawData)) {
        botText = rawData.filter(item => item.type === 'text').map(item => item.text).join('\n')
      } else if (typeof rawData === 'object') {
        botText = rawData.text || JSON.stringify(rawData)
      } else {
        botText = String(rawData)
      }

      setMessages(prev => [...prev, { sender: 'bot', text: botText }])

    } catch (error) {
      console.error("Error:", error)
      setMessages(prev => [...prev, { sender: 'bot', text: "เกิดข้อผิดพลาด ไม่สามารถเชื่อมต่อ Server ได้" }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); 
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      <div className="chat-interface">
        <header className="chat-header">
          <div style={{display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center'}}>
             <h1>AI Assistant</h1>
             <button onClick={handleReset} className="reset-btn" title="ล้างแชท">
               🗑️ Reset
             </button>
          </div>
          
          <div className="mode-switcher">
            <button 
              className={`mode-btn ${chatMode === 'general' ? 'active' : ''}`}
              onClick={() => setChatMode('general')}
            >
              General
            </button>
            <button 
              className={`mode-btn ${chatMode === 'document' ? 'active' : ''}`}
              onClick={() => setChatMode('document')}
            >
              Document
            </button>
          </div>
        </header>

        {/* --- ส่วนแสดงสถานะ Process แยกออกมาตรงนี้ --- */}
        {processStatus && (
            <div className="status-bar fade-in">
                {processStatus}
            </div>
        )}

        {chatMode === 'document' && (
          <div className="upload-section fade-in">
            <div className="file-input-wrapper">
              <label htmlFor="pdf-upload" className="file-label">
                 {selectedFile ? (
                  <span className="file-name" style={{color: 'var(--primary)'}}>
                    📄 รออัปโหลด: {selectedFile.name}
                  </span>
                ) : currentUploadedFile ? (
                  <span className="file-name" style={{color: '#4ade80'}}>
                    ✅ กำลังใช้: {currentUploadedFile}
                  </span>
                ) : (
                  <span>📎 เลือกไฟล์ PDF ใหม่</span>
                )}

                <input 
                    id="pdf-upload" 
                    type="file" 
                    accept=".pdf" 
                    onChange={handleFileChange} 
                    disabled={uploading} 
                    onClick={(e) => { e.target.value = null }} 
                />
              </label>
              {/* ปุ่ม Upload จะ disable เฉพาะตอนกำลังอัปโหลดไฟล์จริงๆ แต่ตอน process embedding จะไม่ยุ่ง */}
              <button onClick={handleUpload} disabled={!selectedFile || uploading} className="action-btn upload-btn">
                {uploading ? 'Working...' : 'Upload'}
              </button>
            </div>
          </div>
        )}

        <div className="chat-box">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>สวัสดีครับ! 👋 {chatMode === 'general' ? 'ถามอะไรก็ได้เลยครับ' : 'อัปโหลดเอกสารแล้วถามได้เลย'}</p>
            </div>
          )}
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.sender}`}>
              <div className="message-bubble">
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message-row bot">
              <div className="message-bubble loading">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)} 
            onKeyDown={handleKeyDown}
            placeholder="พิมพ์ข้อความ..."
            className="chat-textarea"
          />
          <button 
            onClick={sendMessage} 
            disabled={loading || !input.trim()} 
            className="send-btn"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  )
}

export default App