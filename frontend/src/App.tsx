import { useState, useRef, useEffect } from 'react';
import { streamProcessVideo, ProcessResponse } from './lib/api';
import ReactMarkdown from 'react-markdown';
import { Loader2, FileText, Youtube, Settings, Play, Sparkles, HelpCircle, Download } from 'lucide-react';
import { Mermaid } from './components/Mermaid';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ProgressBar } from './components/ProgressBar';
import { FAQModal } from './components/FAQModal';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

function App() {
    const [url, setUrl] = useState('');
    const [mode, setMode] = useState<'local' | 'api'>('local');
    const [tasks, setTasks] = useState<{ transcribe: boolean; summary: boolean }>({ transcribe: true, summary: false });
    const [openaiKey, setOpenaiKey] = useState('');
    const [geminiKey, setGeminiKey] = useState('');

    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<ProcessResponse | null>(null);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState<'transcript' | 'summary'>('transcript');

    // Progress State
    const [stage, setStage] = useState<'idle' | 'downloading' | 'transcribing' | 'summarizing' | 'complete' | 'error'>('idle');
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('');
    const [downloadedBytes, setDownloadedBytes] = useState(0);
    const [totalBytes, setTotalBytes] = useState(0);
    const [downloadSpeed, setDownloadSpeed] = useState(0);
    const [isFAQOpen, setIsFAQOpen] = useState(false);

    const abortControllerRef = useRef<AbortController | null>(null);

    // Reset message when stage changes
    useEffect(() => {
        setProgressMessage('');
    }, [stage]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!url.trim()) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        if (mode === 'api' && !openaiKey.trim()) {
            setError('Cloud API mode requires a Groq API Key');
            return;
        }

        setIsLoading(true);
        setError('');
        setResult(null);
        setStage('downloading');
        setProgress(0);
        setProgressMessage('Initializing...');
        setDownloadedBytes(0);
        setTotalBytes(0);
        setDownloadSpeed(0);

        abortControllerRef.current = new AbortController();

        await streamProcessVideo(
            url,
            mode,
            tasks.summary ? 'summary' : 'transcribe',
            openaiKey,
            geminiKey,
            (event: any) => {
                setStage(event.stage as any);
                setProgress(event.progress);
                if (event.message) setProgressMessage(event.message);
                if (event.downloaded !== undefined) setDownloadedBytes(event.downloaded);
                if (event.total !== undefined) setTotalBytes(event.total);
                if (event.speed !== undefined) setDownloadSpeed(event.speed);
            },
            (data: any) => {
                setResult(data);
                setIsLoading(false);
                setStage('complete');
                if (data.summary) setActiveTab('summary');
            },
            (err: string) => {
                setError(err);
                setIsLoading(false);
                setStage('error');
            },
            abortControllerRef.current?.signal
        );
    };

    return (
        <div className="min-h-screen w-full bg-[#050510] text-zinc-100 flex items-center justify-center p-6 relative overflow-hidden font-sans">
            {/* Background Ambience */}
            <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[128px] pointer-events-none animate-pulse" style={{ animationDuration: '8s' }} />
            <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[128px] pointer-events-none animate-pulse" style={{ animationDuration: '10s', animationDelay: '1s' }} />

            <div className="w-full max-w-4xl relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

                {/* LEFT COLUMN: Controls */}
                <div className="lg:col-span-5 space-y-6">
                    {/* Header */}
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2.5 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl shadow-lg shadow-purple-500/20">
                                <img src="/app_icon.png" alt="Logo" className="w-6 h-6 object-contain" />
                            </div>
                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">
                                YT Abstract
                            </h1>
                        </div>
                        <p className="text-zinc-500 text-sm ml-1">Universal Video Intelligence Engine</p>
                    </div>

                    {/* Settings Panel */}
                    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 space-y-6">

                        {/* URL Input */}
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                                <Youtube className="w-3.5 h-3.5" /> Source URL
                            </label>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="Paste YouTube link here..."
                                className="w-full bg-zinc-950/50 border border-white/10 rounded-xl px-4 py-3 text-sm focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/20 outline-none transition-all placeholder:text-zinc-700 hover:border-white/20"
                            />
                        </div>

                        {/* Config Grid */}
                        <div className="grid grid-cols-2 gap-4">
                            {/* Compute Mode */}
                            <div className="col-span-2 space-y-2">
                                <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                                    <Settings className="w-3.5 h-3.5" /> Compute Engine
                                </label>
                                <div className="grid grid-cols-2 gap-2 bg-zinc-950/50 p-1.5 rounded-xl border border-white/5">
                                    <button
                                        type="button"
                                        onClick={() => setMode('local')}
                                        className={cn(
                                            "flex items-center justify-center gap-2 py-2 px-4 rounded-lg text-sm font-medium transition-all duration-300",
                                            mode === 'local'
                                                ? "bg-zinc-800 text-white shadow-lg"
                                                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                                        )}
                                    >
                                        Local GPU
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setMode('api')}
                                        className={cn(
                                            "flex items-center justify-center gap-2 py-2 px-4 rounded-lg text-sm font-medium transition-all duration-300",
                                            mode === 'api'
                                                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-900/20"
                                                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                                        )}
                                    >
                                        Cloud API
                                    </button>
                                </div>
                            </div>

                            {/* Options */}
                            <div className="col-span-2 flex gap-2">
                                <button
                                    type="button"
                                    onClick={() => setTasks(prev => ({ ...prev, transcribe: !prev.transcribe || prev.summary ? !prev.transcribe : true }))}
                                    className={cn(
                                        "flex-1 py-3 px-4 rounded-xl border text-sm font-medium transition-all duration-300 flex items-center justify-center gap-2",
                                        tasks.transcribe
                                            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                                            : "bg-transparent border-white/5 text-zinc-500 hover:border-white/10"
                                    )}
                                >
                                    <FileText className="w-4 h-4" /> Transcribe
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setTasks(prev => ({ ...prev, summary: !prev.summary }))}
                                    className={cn(
                                        "flex-1 py-3 px-4 rounded-xl border text-sm font-medium transition-all duration-300 flex items-center justify-center gap-2",
                                        tasks.summary
                                            ? "bg-orange-500/10 border-orange-500/30 text-orange-400"
                                            : "bg-transparent border-white/5 text-zinc-500 hover:border-white/10"
                                    )}
                                >
                                    <Sparkles className="w-4 h-4" /> Summary
                                </button>
                            </div>
                        </div>

                        {/* API Keys */}
                        <div className="space-y-4 pt-2 border-t border-white/5">
                            {mode === 'api' && (
                                <div className="space-y-1.5 animate-in fade-in slide-in-from-left-2">
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs text-purple-400 font-medium">Groq API Key</label>
                                        <button type="button" onClick={() => setIsFAQOpen(true)} className="text-xs text-purple-400/60 hover:text-purple-300 flex items-center gap-1 transition-colors">
                                            <HelpCircle className="w-3 h-3" /> Get Key
                                        </button>
                                    </div>
                                    <input
                                        type="password"
                                        value={openaiKey}
                                        onChange={(e) => setOpenaiKey(e.target.value)}
                                        placeholder="gsk_..."
                                        className="w-full bg-zinc-950/50 border border-purple-500/20 rounded-lg px-3 py-2 text-sm focus:border-purple-500/50 outline-none transition-all placeholder:text-zinc-700"
                                    />
                                </div>
                            )}
                            {tasks.summary && (
                                <div className="space-y-1.5 animate-in fade-in slide-in-from-left-2">
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs text-orange-400 font-medium">Gemini API Key</label>
                                        <button type="button" onClick={() => setIsFAQOpen(true)} className="text-xs text-orange-400/60 hover:text-orange-300 flex items-center gap-1 transition-colors">
                                            <HelpCircle className="w-3 h-3" /> Get Key
                                        </button>
                                    </div>
                                    <input
                                        type="password"
                                        value={geminiKey}
                                        onChange={(e) => setGeminiKey(e.target.value)}
                                        placeholder="AIza..."
                                        className="w-full bg-zinc-950/50 border border-orange-500/20 rounded-lg px-3 py-2 text-sm focus:border-orange-500/50 outline-none transition-all placeholder:text-zinc-700"
                                    />
                                </div>
                            )}
                        </div>

                        {/* Action Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 bg-white text-zinc-950 font-bold rounded-xl shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all duration-300 relative overflow-hidden group"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                            {isLoading && stage === 'idle' ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Play className="w-5 h-5 fill-current" />
                            )}
                            <span className="relative z-10">{isLoading ? 'Processing...' : 'Run Analysis'}</span>
                        </button>
                    </form>

                    {/* Progress Bar (Sticky) */}
                    <div className="min-h-[60px]">
                        <ProgressBar
                            stage={stage}
                            progress={progress}
                            message={progressMessage}
                            downloaded={downloadedBytes}
                            total={totalBytes}
                            speed={downloadSpeed}
                            onCancel={() => {
                                if (abortControllerRef.current) {
                                    abortControllerRef.current.abort();
                                    setStage('idle');
                                    setIsLoading(false);
                                    setError('Processing cancelled');
                                }
                            }}
                            mode={mode}
                        />
                    </div>

                    {error && (
                        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-200 rounded-xl text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
                            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                            {error}
                        </div>
                    )}
                </div>

                {/* RIGHT COLUMN: Results */}
                <div className="lg:col-span-7 h-[85vh] flex flex-col glass-panel rounded-3xl overflow-hidden border border-white/5 shadow-2xl relative">
                    {!result ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-zinc-600 p-10 text-center space-y-4">
                            <div className="w-24 h-24 rounded-full bg-zinc-800/50 flex items-center justify-center border border-white/5">
                                <Sparkles className="w-10 h-10 text-zinc-700" />
                            </div>
                            <div>
                                <p className="text-lg font-medium text-zinc-500">Ready to Analyze</p>
                                <p className="text-xs text-zinc-700 mt-2 max-w-xs mx-auto">Results, summaries, and visualizations will appear here after processing.</p>
                            </div>
                        </div>
                    ) : (
                        <>
                            {/* Result Tabs */}
                            <div className="flex items-center justify-between border-b border-white/5 bg-zinc-950/30 backdrop-blur-md sticky top-0 z-10 px-2">
                                <div className="flex flex-1">
                                    <button
                                        onClick={() => setActiveTab('transcript')}
                                        className={cn(
                                            "flex-1 py-4 text-sm font-medium transition-all relative",
                                            activeTab === 'transcript' ? "text-white" : "text-zinc-500 hover:text-zinc-300"
                                        )}
                                    >
                                        Transcript
                                        {activeTab === 'transcript' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />}
                                    </button>
                                    {result.summary && (
                                        <button
                                            onClick={() => setActiveTab('summary')}
                                            className={cn(
                                                "flex-1 py-4 text-sm font-medium transition-all relative",
                                                activeTab === 'summary' ? "text-white" : "text-zinc-500 hover:text-zinc-300"
                                            )}
                                        >
                                            Summary & Mind Map
                                            {activeTab === 'summary' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]" />}
                                        </button>
                                    )}
                                </div>
                                <button
                                    onClick={() => {
                                        if (!result) return;
                                        const content = `# ${result.transcript.slice(0, 50)}...\n\n## Summary\n${result.summary || 'No summary available'}\n\n## Transcript\n${result.transcript}`;
                                        const blob = new Blob([content], { type: 'text/markdown' });
                                        const url = URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = `yt_summary_${Date.now()}.md`;
                                        document.body.appendChild(a);
                                        a.click();
                                        document.body.removeChild(a);
                                        URL.revokeObjectURL(url);
                                    }}
                                    className="mr-2 p-2 hover:bg-white/10 rounded-lg text-zinc-400 hover:text-white transition-colors"
                                    title="Download Results"
                                >
                                    <Download className="w-5 h-5" />
                                </button>
                            </div>


                            {/* Result Content */}
                            <div className="flex-1 overflow-y-auto custom-scrollbar p-8 bg-zinc-950/20">
                                <div className="prose prose-invert max-w-none prose-headings:text-zinc-100 prose-p:text-zinc-300 prose-li:text-zinc-300 prose-strong:text-zinc-100 prose-a:text-blue-400">
                                    {activeTab === 'summary' ? <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                        <ReactMarkdown
                                            components={{
                                                code({ node, inline, className, children, ...props }: any) {
                                                    const match = /language-(\w+)/.exec(className || '');
                                                    const isMermaid = !inline && match && match[1] === 'mermaid';

                                                    if (isMermaid) {
                                                        return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                                                    }
                                                    return <code className={className} {...props}>{children}</code>;
                                                }
                                            }}
                                        >
                                            {result.summary!}
                                        </ReactMarkdown>
                                    </div>
                                        : (
                                            <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-zinc-400 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                                {result.transcript}
                                            </div>
                                        )}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            <FAQModal isOpen={isFAQOpen} onClose={() => setIsFAQOpen(false)} />
        </div >
    );
}

export default App;
