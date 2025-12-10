import React, { useEffect, useRef, useState } from 'react';
import { MessageSquare, X } from 'lucide-react';

const ChatWidget = () => {
    const [open, setOpen] = useState(false);
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Hi! Ask any neuroanatomy or brain-disease question. Answers use the ingested textbook via Pinecone.',
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
    }, [messages, open]);

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
        <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3">
            {open && (
                <div className="w-[360px] max-w-[90vw] overflow-hidden rounded-2xl border border-border/50 bg-white/95 shadow-2xl backdrop-blur">
                    <div className="flex items-center justify-between border-b border-border/50 bg-primary/5 px-4 py-3">
                        <div>
                            <p className="text-sm font-semibold text-foreground">Neuro Chat</p>
                            <p className="text-xs text-muted-foreground">Grounded answers from your neuroanatomy PDF</p>
                        </div>
                        <button
                            type="button"
                            onClick={() => setOpen(false)}
                            className="rounded-full p-1 text-muted-foreground hover:bg-muted/40"
                            aria-label="Close chat"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>

                    <div ref={scrollRef} className="h-[340px] space-y-3 overflow-y-auto px-4 py-3 bg-gradient-to-b from-muted/30 via-white/80 to-muted/30">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`max-w-[90%] rounded-2xl px-3 py-2 text-sm shadow-sm border ${
                                    msg.role === 'assistant'
                                        ? 'bg-primary/5 border-primary/20 text-foreground'
                                        : 'ml-auto bg-secondary text-secondary-foreground border-secondary/40'
                                }`}
                            >
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1 text-[11px] text-muted-foreground">
                                        {msg.sources.map((src, i) => (
                                            <span key={`${src}-${i}`} className="rounded-full border border-border/60 bg-white/85 px-2 py-0.5">
                                                {src || 'unknown source'}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {error && (
                        <div className="border-t border-destructive/30 bg-destructive/10 px-4 py-2 text-xs text-destructive">
                            {error}
                        </div>
                    )}

                    <form onSubmit={sendQuestion} className="border-t border-border/50 bg-muted/30 p-3">
                        <div className="flex items-end gap-2">
                            <textarea
                                className="min-h-[50px] flex-1 resize-none rounded-xl border border-border/60 bg-white px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
                                placeholder="Ask about lesions, vascular territories, syndromes..."
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                            />
                            <button
                                type="submit"
                                disabled={!question.trim() || isLoading}
                                className="btn-primary px-3 py-2 text-sm disabled:cursor-not-allowed"
                            >
                                {isLoading ? '...' : 'Send'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <button
                type="button"
                onClick={() => setOpen((v) => !v)}
                className="flex items-center gap-2 rounded-full bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-lg hover:shadow-xl"
                aria-label="Open chat"
            >
                <MessageSquare className="h-4 w-4" />
                {open ? 'Hide chat' : 'Ask a question'}
            </button>
        </div>
    );
};

export default ChatWidget;
