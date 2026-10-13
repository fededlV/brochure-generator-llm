import {
  GenerationRequest,
  StatusEventData,
  LinksSelectedEventData,
  TokenEventData,
  CompleteEventData,
  ErrorEventData,
} from '../types';

export interface StreamCallbacks {
  onStatus?: (data: StatusEventData) => void;
  onLinksSelected?: (data: LinksSelectedEventData) => void;
  onToken?: (data: TokenEventData) => void;
  onComplete?: (data: CompleteEventData) => void;
  onError?: (data: ErrorEventData) => void;
}

export async function checkBackendHealth() {
  try {
    const res = await fetch('/api/health');
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    return { status: 'error', gemini_configured: false, model: 'unknown' };
  }
}

export async function streamBrochureGeneration(
  request: GenerationRequest,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch('/api/generate/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok) {
    const errText = await response.text();
    callbacks.onError?.({
      error: `Server responded with ${response.status}: ${errText || response.statusText}`,
    });
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    callbacks.onError?.({ error: 'Response body is not readable' });
    return;
  }

  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() || '';

      for (const block of blocks) {
        if (!block.trim()) continue;

        let eventName = 'message';
        let dataStr = '';

        const lines = block.split('\n');
        for (const line of lines) {
          if (line.startsWith('event:')) {
            eventName = line.replace('event:', '').trim();
          } else if (line.startsWith('data:')) {
            dataStr = line.replace('data:', '').trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          switch (eventName) {
            case 'status':
              callbacks.onStatus?.(parsed as StatusEventData);
              break;
            case 'links_selected':
              callbacks.onLinksSelected?.(parsed as LinksSelectedEventData);
              break;
            case 'token':
              callbacks.onToken?.(parsed as TokenEventData);
              break;
            case 'complete':
              callbacks.onComplete?.(parsed as CompleteEventData);
              break;
            case 'error':
              callbacks.onError?.(parsed as ErrorEventData);
              break;
            default:
              break;
          }
        } catch (parseError) {
          console.warn('Failed to parse SSE payload:', dataStr, parseError);
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      callbacks.onError?.({ error: 'Generation stopped by user.' });
    } else {
      callbacks.onError?.({ error: err.message || 'Stream connection error' });
    }
  } finally {
    reader.releaseLock();
  }
}
