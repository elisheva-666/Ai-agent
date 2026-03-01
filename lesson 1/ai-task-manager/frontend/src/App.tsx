import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', content: 'שלום! אני העוזר האישי שלך לניהול משימות. מה תרצי לעשות היום?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    // הוספת הודעת המשתמש למסך
    const newMessages = [...messages, { role: 'user', content: input }]
    setMessages(newMessages)
    setInput('')
    setIsLoading(true)

    try {
      // שליחת הבקשה לשרת הפייתון שלנו
      const response = await axios.post('http://127.0.0.1:8000/chat', {
        message: input
      })

      // הוספת תגובת ה-Agent למסך
      setMessages([...newMessages, { role: 'agent', content: response.data.reply }])
    } catch (error) {
      console.error("Error communicating with server:", error)
      setMessages([...newMessages, { role: 'agent', content: 'אופס, הייתה שגיאה בתקשורת עם השרת. אנא בדקי שהשרת רץ.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <h1>ניהול משימות AI 🤖</h1>
      
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {isLoading && <div className="message agent">מקליד... ✍️</div>}
      </div>

      <div className="input-area">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="כתבי כאן משימה (למשל: תזכיר לי לקנות חלב מחר)..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          שלח
        </button>
      </div>
    </div>
  )
}

export default App