import { useState } from 'react';
import { streamProcessVideo, ProcessResponse } from './lib/api';
import ReactMarkdown from 'react-markdown';
import { Loader2, Download, Settings2, FileText, Youtube } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ProgressBar } from './components/ProgressBar';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

function App() {
    const [url, setUrl] = useState('');
    const [mode, setMode] = useState<'local' | 'api'>('local');
    const [taskType, setTaskType] = useState<'transcribe' | 'summary'>('transcribe');
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

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Input Validation
        if (!url.trim()) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        setIsLoading(true);
        setError('');
        setResult(null);
        setStage('downloading');
        setProgress(0);
        setProgressMessage('Initializing...');

        await streamProcessVideo(
            url,
            mode,
            taskType,
            mode === 'api' ? openaiKey : undefined,
            taskType === 'summary' ? geminiKey : undefined,
            // onProgress
            (event) => {
                setStage(event.stage);
                setProgress(event.progress);
                if (event.message) setProgressMessage(event.message);
            },
            // onResult
            (data) => {
                setResult(data);
                setStage('complete');
                setProgress(100);
                setIsLoading(false);
                if (taskType === 'summary') setActiveTab('summary');
            },
            // onError
            (err) => {
                setError(err);
                setStage('error');
                setIsLoading(false);
            }
        );
    };

    const handleDownload = () => {
        if (!result) return;
        const content = activeTab === 'summary' ? result.summary : result.transcript;
        if (!content) return;

        const blob = new Blob([content], { type: 'text/markdown' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `yt-abstract-${activeTab}-${Date.now()}.md`;
        link.click();
    };

    return (
        <div className="min-h-screen bg-zinc-950 text-white p-8 font-sans selection:bg-blue-500/30">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <header className="flex items-center gap-3">
                    <div className="p-3 bg-blue-600/20 rounded-xl border border-blue-500/20">
                        <Youtube className="w-8 h-8 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                            YT Abstract
                        </h1>
                        <p className="text-zinc-400 text-sm">Design driven workflow for video summarization</p>
                    </div>
                </header>

                {/* Input Card */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                    <form onSubmit={handleSubmit} className="space-y-6">

                        {/* URL Input */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">YouTube URL</label>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => {
                                    setUrl(e.target.value);
                                    if (error) setError('');
                                }}
                                placeholder="https://www.youtube.com/watch?v=..."
                                className={cn(
                                    "w-full bg-zinc-950 border rounded-lg px-4 py-3 focus:ring-2 outline-none transition-all placeholder:text-zinc-600",
                                    error
                                        ? "border-red-500/50 focus:border-red-500 focus:ring-red-500/20"
                                        : "border-zinc-800 focus:ring-blue-500/50 focus:border-blue-500"
                                )}
                            />
                        </div>

                        {/* Config Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-zinc-950/50 rounded-xl border border-zinc-800/50">

                            {/* Computing Mode */}
                            <div className="space-y-3">
                                <label className="flex items-center gap-2 text-sm font-medium text-zinc-400">
                                    <Settings2 className="w-4 h-4" />
                                    Computing Mode
                                </label>
                                <div className="flex bg-zinc-900 p-1 rounded-lg border border-zinc-800">
                                    <button
                                        type="button"
                                        onClick={() => setMode('local')}
                                        className={cn(
                                            "flex-1 py-2 text-sm font-medium rounded-md transition-all",
                                            mode === 'local' ? "bg-blue-600 text-white shadow-lg" : "text-zinc-400 hover:text-white"
                                        )}
                                    >
                                        Local GPU
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setMode('api')}
                                        className={cn(
                                            "flex-1 py-2 text-sm font-medium rounded-md transition-all",
                                            mode === 'api' ? "bg-purple-600 text-white shadow-lg" : "text-zinc-400 hover:text-white"
                                        )}
                                    >
                                        Cloud API
                                    </button>
                                </div>
                            </div>

                            {/* Task Type */}
                            <div className="space-y-3">
                                <label className="flex items-center gap-2 text-sm font-medium text-zinc-400">
                                    <FileText className="w-4 h-4" />
                                    Task Type
                                </label>
                                <div className="flex bg-zinc-900 p-1 rounded-lg border border-zinc-800">
                                    <button
                                        type="button"
                                        onClick={() => setTaskType('transcribe')}
                                        className={cn(
                                            "flex-1 py-2 text-sm font-medium rounded-md transition-all",
                                            taskType === 'transcribe' ? "bg-emerald-600 text-white shadow-lg" : "text-zinc-400 hover:text-white"
                                        )}
                                    >
                                        Transcribe
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setTaskType('summary')}
                                        className={cn(
                                            "flex-1 py-2 text-sm font-medium rounded-md transition-all",
                                            taskType === 'summary' ? "bg-orange-600 text-white shadow-lg" : "text-zinc-400 hover:text-white"
                                        )}
                                    >
                                        + Summary
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* API Keys (Conditional) */}
                        <div className="space-y-4">
                            {mode === 'api' && (
                                <div className="animate-in fade-in slide-in-from-top-2">
                                    <label className="text-xs text-purple-400 mb-1 block">OpenAI / Groq API Key</label>
                                    <input
                                        type="password"
                                        value={openaiKey}
                                        onChange={(e) => setOpenaiKey(e.target.value)}
                                        placeholder="sk-..."
                                        className="w-full bg-zinc-950 border border-purple-500/30 rounded-lg px-4 py-2 focus:border-purple-500 outline-none text-sm"
                                    />
                                </div>
                            )}
                            {taskType === 'summary' && (
                                <div className="animate-in fade-in slide-in-from-top-2">
                                    <label className="text-xs text-orange-400 mb-1 block">Gemini API Key</label>
                                    <input
                                        type="password"
                                        value={geminiKey}
                                        onChange={(e) => setGeminiKey(e.target.value)}
                                        placeholder="AIza..."
                                        className="w-full bg-zinc-950 border border-orange-500/30 rounded-lg px-4 py-2 focus:border-orange-500 outline-none text-sm"
                                    />
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
                        >
                            {isLoading && stage === 'idle' ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing Video...
                                </>
                            ) : (
                                "Start Processing"
                            )}
                        </button>

                        {/* Progress Bar */}
                        <ProgressBar stage={stage} progress={progress} message={progressMessage} />

                        {error && (
                            <div className="p-4 bg-red-900/20 border border-red-500/30 text-red-400 rounded-lg text-sm text-center animate-in fade-in">
                                {error}
                            </div>
                        )}

                    </form>
                </div>

                {/* Results Area */}
                {result && (
                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl overflow-hidden shadow-xl animate-in fade-in slide-in-from-bottom-4">
                        <div className="flex border-b border-zinc-800 bg-zinc-950/50">
                            <button
                                onClick={() => setActiveTab('transcript')}
                                className={cn(
                                    "px-6 py-4 text-sm font-medium border-b-2 transition-all",
                                    activeTab === 'transcript' ? "border-blue-500 text-blue-400" : "border-transparent text-zinc-400 hover:text-white"
                                )}
                            >
                                Transcript
                            </button>
                            {result.summary && (
                                <button
                                    onClick={() => setActiveTab('summary')}
                                    className={cn(
                                        "px-6 py-4 text-sm font-medium border-b-2 transition-all",
                                        activeTab === 'summary' ? "border-orange-500 text-orange-400" : "border-transparent text-zinc-400 hover:text-white"
                                    )}
                                >
                                    Summary
                                </button>
                            )}
                            <div className="ml-auto flex items-center pr-4">
                                <button
                                    onClick={handleDownload}
                                    className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
                                    title="Download .md"
                                >
                                    <Download className="w-5 h-5" />
                                </button>
                            </div>
                        </div>

                        <div className="p-8 max-h-[600px] overflow-y-auto custom-scrollbar">
                            <div className="prose prose-invert max-w-none prose-headings:text-zinc-200 prose-p:text-zinc-400 prose-li:text-zinc-400 prose-strong:text-zinc-200">
                                {activeTab === 'summary' ? (
                                    <ReactMarkdown>{result.summary!}</ReactMarkdown>
                                ) : (
                                    <div className="whitespace-pre-wrap">{result.transcript}</div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    )
}

export default App
