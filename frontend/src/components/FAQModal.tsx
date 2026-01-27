import React from 'react';
import { X, ExternalLink, HelpCircle, Terminal } from 'lucide-react';
import { cn } from '../lib/utils';

interface FAQModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function FAQModal({ isOpen, onClose }: FAQModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
            <div
                className="relative w-full max-w-2xl bg-zinc-900/90 border border-white/10 rounded-2xl shadow-2xl p-8 animate-in zoom-in-95 duration-300"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Decoration */}
                <div className="absolute -top-20 -right-20 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />

                <button
                    onClick={onClose}
                    className="absolute top-6 right-6 p-2 rounded-full hover:bg-white/5 text-zinc-400 hover:text-white transition-all"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="flex items-center gap-3 mb-8">
                    <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
                        <HelpCircle className="w-6 h-6" />
                    </div>
                    <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-zinc-400">
                        常見問題 (FAQ)
                    </h2>
                </div>

                <div className="space-y-8 max-h-[60vh] overflow-y-auto custom-scrollbar pr-2">

                    {/* Groq Section */}
                    <div className="space-y-3">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-purple-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                            如何申請 Groq API Key？
                        </h3>
                        <div className="glass-panel p-5 rounded-xl space-y-4">
                            <p className="text-zinc-400 text-sm">Groq 提供極速的 AI 推論服務，目前有免費額度。</p>
                            <ol className="list-decimal list-inside text-zinc-300 space-y-2 text-sm ml-2">
                                <li>前往 <span className="text-white font-medium">Groq Console</span>。</li>
                                <li>使用 Google 帳號登入。</li>
                                <li>點擊 <span className="text-purple-300 border border-purple-500/30 px-1.5 py-0.5 rounded text-xs">Create API Key</span>。</li>
                                <li>複製 <code>gsk_</code> 開頭的金鑰。</li>
                            </ol>
                            <a
                                href="https://console.groq.com/keys"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors bg-purple-500/10 px-3 py-2 rounded-lg hover:bg-purple-500/20 border border-purple-500/20"
                            >
                                前往 Groq Console <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>

                    {/* Gemini Section */}
                    <div className="space-y-3">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-orange-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
                            如何申請 Gemini API Key？
                        </h3>
                        <div className="glass-panel p-5 rounded-xl space-y-4">
                            <p className="text-zinc-400 text-sm">Google Gemini 目前對開發者提供免費額度。</p>
                            <ol className="list-decimal list-inside text-zinc-300 space-y-2 text-sm ml-2">
                                <li>前往 <span className="text-white font-medium">Google AI Studio</span>。</li>
                                <li>點擊左上角 <span className="text-orange-300 border border-orange-500/30 px-1.5 py-0.5 rounded text-xs">Get API key</span>。</li>
                                <li>點擊 <strong>Create API key in new project</strong>。</li>
                                <li>複製 <code>AIza</code> 開頭的金鑰。</li>
                            </ol>
                            <a
                                href="https://aistudio.google.com/app/apikey"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-xs font-medium text-orange-400 hover:text-orange-300 transition-colors bg-orange-500/10 px-3 py-2 rounded-lg hover:bg-orange-500/20 border border-orange-500/20"
                            >
                                前往 AI Studio <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>

                    {/* GPU Section */}
                    <div className="space-y-3">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-cyan-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                            Local GPU 需求
                        </h3>
                        <p className="text-zinc-400 text-sm leading-relaxed p-4 rounded-xl border border-white/5 bg-white/5">
                            需要 NVIDIA 顯示卡 (如 RTX 3060, 4060) 並安裝最新驅動。此模式完全離線運行，不需要 API Key。
                        </p>
                    </div>
                </div>

                <div className="mt-8 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 bg-zinc-100 hover:bg-white text-zinc-900 rounded-xl transition-all font-semibold shadow-lg shadow-white/5 active:scale-95"
                    >
                        知道了
                    </button>
                </div>
            </div>
        </div>
    );
}
