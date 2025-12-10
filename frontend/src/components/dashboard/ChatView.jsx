import React, { useEffect, useRef, useState } from 'react';

const ChatView = () => {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Ask any neuroanatomy or brain-disease question. I will answer from the uploaded textbook context.',
            sources: [],
        },
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const sendQuestion = async (e) => {
        e.preventDefault();
        const trimmed = question.trim();
        if (!trimmed || isLoading) return;

        setError('');
        setIsLoading(true);
        const userMessage = { role: 'user', content: trimmed };
        setMessages((prev) => [...prev, userMessage]);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: trimmed }),
            });

            const text = await response.text();
            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (parseErr) {
                data = { error: text || 'Invalid JSON from server' };
            }

            if (!response.ok) {
                const detail = data?.error || data?.detail || `HTTP ${response.status}`;
                throw new Error(detail);
            }

            const assistantMessage = {
                role: 'assistant',
                content: data.answer || 'No answer returned.',
                sources: data.sources || [],
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setQuestion('');
        } catch (err) {
            console.error(err);
            setError(err.message || 'Unable to fetch answer. Check the backend and try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-full flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold">Neuro RAG Chat</h1>
                <p className="mt-2 text-muted-foreground">
                    Grounded answers from your ingested neuroanatomy textbook and Pinecone.
                </p>
            </div>

            <div className="flex-1 overflow-hidden rounded-3xl border border-border/50 bg-white/90 text-foreground shadow-lg backdrop-blur">
                <div ref={scrollRef} className="h-[420px] overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-muted/30 via-white/80 to-muted/30">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`max-w-3xl rounded-2xl px-4 py-3 shadow-sm border ${
                                msg.role === 'assistant'
                                    ? 'bg-primary/5 border-primary/20 text-foreground'
                                    : 'bg-secondary text-secondary-foreground ml-auto border-secondary/40'
                            }`}
                        >
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
                                    {msg.sources.map((src, i) => (
                                        <span key={`${src}-${i}`} className="rounded-full bg-white/80 px-3 py-1 border border-border/60">
                                            {src || 'unknown source'}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                {error && (
                    <div className="border-t border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                        {error}
                    </div>
                )}
                <form onSubmit={sendQuestion} className="border-t border-border/50 bg-muted/30 p-4">
                    <div className="flex items-end gap-3">
                        <textarea
                            className="min-h-[60px] flex-1 resize-none rounded-2xl border border-border/60 bg-white px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
                            placeholder="Ask about neuroanatomy, lesions, vascular territories, or clinical syndromes..."
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                        />
                        <button
                            type="submit"
                            disabled={!question.trim() || isLoading}
                            className="btn-primary px-4 py-2 text-sm disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Thinking…' : 'Send'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ChatView;
