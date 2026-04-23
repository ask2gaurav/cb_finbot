import { useState, useRef, useEffect } from "react";
import { useAuthStore } from "../lib/auth";
import { useNavigate } from "react-router";

export default function Chat() {
  const { token, role, logout } = useAuthStore();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token) navigate("/login");
  }, [token, navigate]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom() }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !token) return;

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    const asstMsgIndex = messages.length + 1;
    setMessages(prev => [...prev, { role: "assistant", content: "", streaming: true }]);

    try {
      const response = await fetch("/api/v1/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ message: input })
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let done = false;
      let streamedResponse = "";
      
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunkStr = decoder.decode(value, { stream: true });
          const events = chunkStr.split("\\n\\n").filter((e: string) => e.startsWith("data: "));
          
          for (const ev of events) {
            const dataStr = ev.replace("data: ", "");
            try {
              const data = JSON.parse(dataStr);
              if (data.type === "token") {
                streamedResponse += data.content;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[asstMsgIndex] = { ...newMsgs[asstMsgIndex], content: streamedResponse };
                  return newMsgs;
                });
              } else if (data.type === "done") {
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[asstMsgIndex] = {
                    role: "assistant",
                    content: data.final_answer,
                    sources: data.sources,
                    flags: data.guardrail_flags,
                    blocked: data.blocked,
                    streaming: false
                  };
                  return newMsgs;
                });
              } else if (data.type === "error") {
                console.error("Stream error", data.content);
              }
            } catch (e) {
                // incomplete chunks or JSON parse errors
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex bg-gray-100" style={{ height: '100vh' }}>
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex flex-col hidden sm:flex">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold">RAG Platform</h1>
          <div className="mt-2 flex items-center gap-2">
            <span className="px-2 py-1 text-xs bg-blue-600 rounded-full">{role}</span>
          </div>
        </div>
        <div className="p-4 flex-1">
          {role === 'admin' && (
             <button onClick={() => navigate('/admin/users')} className="w-full py-2 mb-2 bg-gray-800 rounded hover:bg-gray-700 text-sm">
               Admin Panel
             </button>
          )}
        </div>
        <div className="p-4 border-t border-gray-800">
          <button onClick={() => { logout(); navigate("/login"); }} className="w-full py-2 bg-red-600 rounded text-sm font-semibold hover:bg-red-700">
            Sign out
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative min-w-0 h-full">
         <div className="flex-1 overflow-y-auto p-4 space-y-6">
           {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-500">
                <p>Start a conversation. Note your role limits your knowledge access.</p>
              </div>
           ) : (
              messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-2xl rounded-2xl p-4 ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white shadow border border-gray-200 text-gray-800'}`}>
                    <p className="whitespace-pre-wrap">{m.content}</p>
                    
                    {m.flags && m.flags.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-red-200">
                        <span className="text-xs text-red-600 font-semibold bg-red-50 px-2 py-1 rounded flex gap-1 items-center">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                          Guardrails Flagged: {m.flags.join(", ")}
                        </span>
                      </div>
                    )}
                    
                    {m.sources && m.sources.length > 0 && !m.streaming && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs font-semibold text-gray-500 mb-2">Sources Referenced:</p>
                        <div className="space-y-2">
                          {m.sources.map((src: any, idx: number) => (
                            <details key={idx} className="text-xs bg-gray-50 rounded p-2">
                              <summary className="cursor-pointer font-medium hover:text-blue-600">
                                {src.filename} (p. {src.page})
                              </summary>
                              <div className="mt-2 text-gray-600 italic break-words whitespace-pre-wrap">
                                "{src.text}"
                              </div>
                            </details>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
           )}
           {isTyping && (
             <div className="flex justify-start">
                <div className="bg-white shadow border border-gray-200 rounded-2xl p-4 text-gray-500 text-sm flex gap-1 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '100ms'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '200ms'}}></div>
                </div>
             </div>
           )}
           <div ref={messagesEndRef} />
         </div>
         
         {/* Input Box */}
         <div className="p-4 bg-white border-t border-gray-200">
           <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-end gap-2 bg-gray-50 rounded-xl border border-gray-300 p-2 focus-within:ring-1 focus-within:ring-blue-500">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message RAG assistant... (Shift+Enter for new line)"
                className="w-full max-h-32 bg-transparent border-0 focus:ring-0 resize-none py-2 px-3 sm:text-sm outline-none"
                rows={1}
                style={{ minHeight: '44px' }}
              />
              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="shrink-0 inline-flex items-center justify-center rounded-lg bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
               >
                 <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
               </button>
           </form>
         </div>
      </div>
    </div>
  );
}
