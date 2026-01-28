import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // Proxy handled by Vite
});

export interface ProcessResponse {
    status: string;
    transcript: string;
    summary?: string;
}

// SSE Event Types
export type ProgressEvent = {
    stage: 'downloading' | 'transcribing' | 'summarizing';
    progress: number;
    message?: string;
    // Download-specific fields
    downloaded?: number;  // bytes downloaded
    total?: number;       // total bytes
    speed?: number;       // bytes per second
}

export type ResultEvent = {
    transcript: string;
    summary?: string;
}

export const processVideo = async (
    url: string,
    mode: 'local' | 'api',
    taskType: 'transcribe' | 'summary',
    openaiApiKey?: string,
    geminiApiKey?: string
) => {
    const response = await api.post<ProcessResponse>('/process', {
        url,
        mode,
        task_type: taskType,
        openai_api_key: openaiApiKey,
        gemini_api_key: geminiApiKey,
    });
    return response.data;
};

// Stream Processor using fetch
export const streamProcessVideo = async (
    url: string,
    mode: 'local' | 'api',
    taskType: 'transcribe' | 'summary',
    openaiApiKey: string | undefined,
    geminiApiKey: string | undefined,
    onProgress: (event: ProgressEvent) => void,
    onResult: (result: ResultEvent) => void,
    onError: (error: string) => void,
    abortSignal?: AbortSignal
) => {
    try {
        const response = await fetch('/api/process_stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                mode,
                task_type: taskType,
                openai_api_key: openaiApiKey,
                gemini_api_key: geminiApiKey,
            }),
            signal: abortSignal,
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) throw new Error("No response body");

        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            // Process SSE events manually
            const lines = buffer.split('\n');
            // Keep the last partial line in buffer
            buffer = lines.pop() || '';

            let currentEvent: string | null = null;

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    currentEvent = line.slice(7).trim();
                } else if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6);
                    try {
                        const data = JSON.parse(dataStr);

                        if (currentEvent === 'progress') {
                            onProgress(data);
                        } else if (currentEvent === 'result') {
                            onResult(data);
                        } else if (currentEvent === 'error') {
                            onError(typeof data === 'string' ? data : JSON.stringify(data));
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE data:', dataStr);
                    }
                    currentEvent = null; // Reset for next event
                }
            }
        }
    } catch (err: any) {
        onError(err.message || "Network Error");
    }
};
