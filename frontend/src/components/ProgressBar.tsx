import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Loader2, X, Download, Server, Cloud } from "lucide-react";

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

function formatBytes(bytes: number): string {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function formatSpeed(bytesPerSecond: number): string {
    if (bytesPerSecond === 0) return "";
    return formatBytes(bytesPerSecond) + "/s";
}

interface ProgressBarProps {
    stage: "idle" | "downloading" | "transcribing" | "summarizing" | "complete" | "error";
    progress: number;
    message?: string;
    downloaded?: number;
    total?: number;
    speed?: number;
    onCancel?: () => void;
    mode?: "local" | "api";
}

export function ProgressBar({
    stage,
    progress,
    message,
    downloaded,
    total,
    speed,
    onCancel,
    mode,
}: ProgressBarProps) {
    const getStageColor = () => {
        switch (stage) {
            case "downloading": return "bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.5)]";
            case "transcribing": return "bg-violet-500 shadow-[0_0_15px_rgba(139,92,246,0.5)]";
            case "summarizing": return "bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)]";
            case "complete": return "bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)]";
            case "error": return "bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]";
            default: return "bg-zinc-700";
        }
    };

    const getStatusText = () => {
        if (message) return message; // Prioritize explicit message
        switch (stage) {
            case "downloading": return "Downloading Resources";
            case "transcribing": return mode === "api" ? "Transcribing (Cloud)" : "Transcribing (Local GPU)";
            case "summarizing": return "Synthesizing Summary";
            case "complete": return "Task Completed";
            case "error": return "Process Failed";
            default: return "Initializing";
        }
    };

    const getStatusIcon = () => {
        switch (stage) {
            case "downloading": return <Download className="w-4 h-4 animate-bounce" />;
            case "transcribing": return mode === "api" ? <Cloud className="w-4 h-4 animate-pulse" /> : <Server className="w-4 h-4 animate-pulse" />;
            case "summarizing": return <Loader2 className="w-4 h-4 animate-spin" />;
            case "complete": return null;
            default: return <Loader2 className="w-4 h-4 animate-spin" />;
        }
    };

    const isProcessing = stage !== "idle" && stage !== "complete" && stage !== "error";
    // Only use indeterminate if we are summarizing (no progress usually) or explicitly indeterminate.
    // For downloading/transcribing, we usually want to show 0% if it's 0.
    // But if progress is 0 for a long time, user gets anxious.
    // Let's keep indeterminate but make it a full-width subtle pulse instead of a moving bar?
    // OR just remove the 1/3 width bar.
    // The user said "starts in middle is weird".
    // Let's use a "stripes" animation for indefinite?
    // Actually, "Preparing..." text + 0% bar is clear enough.
    // So let's only use indeterminate for 'summarizing'.
    const isIndefinite = stage === 'summarizing';

    // Explicit check for undefined to allow 0
    const hasDownloadInfo = downloaded !== undefined;
    const downloadDetails = stage === "downloading" && hasDownloadInfo
        ? `${formatBytes(downloaded)}${total ? ` / ${formatBytes(total)}` : ""} • ${formatSpeed(speed || 0)}`
        : null;

    if (stage === "idle") return null;

    return (
        <div className="w-full relative group animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Background Glow */}
            <div className={cn(
                "absolute -inset-1 rounded-lg opacity-20 blur-lg transition-all duration-1000",
                getStageColor().split(" ")[0]
            )} />

            <div className="relative space-y-3 bg-zinc-900/50 p-4 rounded-xl border border-white/5">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className={cn(
                            "p-2 rounded-lg bg-white/5 text-white/80 ring-1 ring-white/10",
                            stage === 'error' && "bg-red-500/10 text-red-500 ring-red-500/20"
                        )}>
                            {getStatusIcon()}
                        </div>
                        <div className="flex flex-col">
                            <span className={cn(
                                "text-sm font-medium tracking-wide",
                                stage === 'error' ? "text-red-400" : "text-zinc-200"
                            )}>
                                {getStatusText()}
                            </span>
                            {downloadDetails && (
                                <span className="text-xs font-mono text-cyan-400 mt-0.5 font-medium tracking-wide shadow-black drop-shadow-md">{downloadDetails}</span>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <span className="text-2xl font-light text-zinc-400 tabular-nums tracking-tighter">
                            {isIndefinite ? "..." : `${Math.round(progress)}%`}
                        </span>
                        {isProcessing && onCancel && (
                            <button
                                onClick={onCancel}
                                className="p-2 rounded-full hover:bg-white/10 text-zinc-500 hover:text-white transition-all active:scale-95"
                                title="Cancel"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Bar */}
                <div className="h-1.5 w-full bg-zinc-950/50 rounded-full overflow-hidden ring-1 ring-white/10 backdrop-blur-sm">
                    {isIndefinite ? (
                        <div className={cn("h-full w-full rounded-full animate-pulse", getStageColor())} />
                    ) : (
                        <div
                            className={cn("h-full transition-all duration-300 ease-out rounded-full shadow-[0_0_10px_currentColor]", getStageColor())}
                            style={{ width: `${Math.max(progress, 2)}%` }} // Minimum 2% visibility
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
