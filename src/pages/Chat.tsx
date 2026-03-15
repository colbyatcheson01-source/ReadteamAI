import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Terminal, Loader2, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  actions?: Array<{
    type: string;
    tool: string;
    description: string;
  }>;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Greetings! I'm your Red Team AI Assistant.

I can help you with:
• **Network Scanning** - Discover hosts and open ports
• **Vulnerability Assessment** - Find weaknesses in targets
• **Exploitation** - Execute attacks with Metasploit
• **Password Attacks** - Brute-force credentials with Hydra
• **Hash Capture** - Use Responder for LLMNR poisoning
• **AD Enumeration** - Analyze Active Directory with BloodHound

What would you like to do today?

**Note:** This assistant uses LM Studio for AI responses. Make sure LM Studio is running with a model loaded.`
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lmStudioStatus, setLmStudioStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check LM Studio status on mount
  useEffect(() => {
    fetch('/api/ai/status')
      .then(res => res.json())
      .then(data => {
        setLmStudioStatus(data.status === 'connected' ? 'connected' : 'disconnected');
      })
      .catch(() => setLmStudioStatus('disconnected'));
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        actions: data.actions
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 p-4 bg-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/20 rounded-lg">
              <Bot className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Red Team AI Assistant</h1>
              <p className="text-sm text-slate-400">Interactive security operations assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              lmStudioStatus === 'connected' ? 'bg-green-500' : 
              lmStudioStatus === 'checking' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
            }`}></span>
            <span className="text-xs text-slate-400">
              {lmStudioStatus === 'connected' ? 'LM Studio Connected' : 
               lmStudioStatus === 'checking' ? 'Checking...' : 'LM Studio Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.role === 'user' 
                ? 'bg-cyan-500/20' 
                : 'bg-purple-500/20'
            }`}>
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-cyan-400" />
              ) : (
                <Sparkles className="w-4 h-4 text-purple-400" />
              )}
            </div>
            <div className={`max-w-[80%] rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-cyan-500/10 border border-cyan-500/20'
                : 'bg-slate-800 border border-slate-700'
            }`}>
              <div className="text-white whitespace-pre-wrap">{message.content}</div>
              
              {/* Action buttons for AI suggestions */}
              {message.actions && message.actions.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-600">
                  <p className="text-xs text-slate-400 mb-2">Suggested Actions:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.actions.map((action, idx) => (
                      <button
                        key={idx}
                        className="px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-md transition-colors flex items-center gap-2"
                      >
                        <Terminal className="w-3 h-3" />
                        {action.tool}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-purple-400" />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-slate-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-700 p-4 bg-slate-800">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about security operations..."
            className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-xs text-slate-500 mt-2 text-center">
          Press Enter to send • The AI can assist with Nmap, Metasploit, SQLMap, Hydra, Responder, and more
        </p>
      </div>
    </div>
  );
}
