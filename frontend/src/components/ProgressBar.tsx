import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Loader2 } from 'lucide-react';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

interface ProgressBarProps {
    stage: 'idle' | 'downloading' | 'transcribing' | 'summarizing' | 'complete' | 'error';
    progress: number; // 0-100
    message?: string;
}

export function ProgressBar({ stage, progress, message }: ProgressBarProps) {
    // Map stage to color
    const getStageColor = () => {
        switch (stage) {
            case 'downloading': return 'bg-cyan-500';
            case 'transcribing': return 'bg-blue-600';
            case 'summarizing': return 'bg-orange-500';
            case 'complete': return 'bg-emerald-500';
            case 'error': return 'bg-red-500';
            default: return 'bg-zinc-700';
        }
    };

    const isProcessing = stage !== 'idle' && stage !== 'complete' && stage !== 'error';

    if (stage === 'idle') return null;

    return (
        <div className="w-full space-y-2 animate-in fade-in slide-in-from-bottom-2">
            <div className="flex justify-between text-sm">
                <span className={cn(
                    "font-medium flex items-center gap-2",
                    stage === 'error' ? "text-red-400" : "text-zinc-300"
                )}>
                    {isProcessing && <Loader2 className="w-3 h-3 animate-spin" />}
                    {stage === 'downloading' && "Downloading Audio..."}
                    {stage === 'transcribing' && "Transcribing (Local GPU)..."}
                    {stage === 'summarizing' && "Generating Summary..."}
                    {stage === 'complete' && "Processing Complete!"}
                    {stage === 'error' && "Error Occurred"}
                </span>
                <span className="text-zinc-500 font-mono">{Math.round(progress)}%</span>
            </div>

            <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div
                    className={cn(
                        "h-full transition-all duration-300 ease-out",
                        getStageColor()
                    )}
                    style={{ width: `${progress}%` }}
                />
            </div>

            {message && (
                <p className="text-xs text-zinc-500 text-right">{message}</p>
            )}
        </div>
    );
}
