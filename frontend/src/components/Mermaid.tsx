import mermaid from 'mermaid';
import { useEffect, useRef, useState } from 'react';

mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    fontFamily: 'inherit',
});

interface MermaidProps {
    chart: string;
}

export const Mermaid = ({ chart }: MermaidProps) => {
    const ref = useRef<HTMLDivElement>(null);
    const [svg, setSvg] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const renderChart = async () => {
            if (!chart) return;
            try {
                // Ensure unique ID for multiple charts
                const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
                const { svg } = await mermaid.render(id, chart);
                setSvg(svg);
                setError(null);
            } catch (err) {
                console.error("Mermaid Render Error:", err);
                setError("Failed to render diagram");
                setSvg('');
            }
        };

        renderChart();
    }, [chart]);

    if (error) {
        return (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-xs font-mono whitespace-pre-wrap">
                <span className="font-bold">Mind Map Error:</span> {error}
                <div className="mt-2 text-zinc-500 text-[10px] bg-zinc-950 p-2 rounded overflow-auto max-h-32">
                    {chart}
                </div>
            </div>
        );
    }

    return (
        <div
            ref={ref}
            className="mermaid overflow-x-auto py-6 flex justify-center bg-zinc-950/30 rounded-xl border border-white/5 my-4 shadow-inner min-h-[100px]"
            dangerouslySetInnerHTML={{ __html: svg }}
        />
    );
};
