export type Audience = 'general' | 'prospects' | 'investors' | 'candidates';
export type Tone = 'professional' | 'energetic' | 'minimalist';

export type PipelineStep =
  | 'idle'
  | 'validating'
  | 'crawling_landing'
  | 'analyzing_links'
  | 'crawling_subpages'
  | 'generating_brochure'
  | 'completed'
  | 'error';

export interface SelectedLink {
  url: string;
  reason: string;
}

export interface GenerationRequest {
  url: string;
  audience: Audience;
  tone: Tone;
  max_subpages: number;
}

export interface StatusEventData {
  step: PipelineStep;
  message: string;
  progress: number;
}

export interface LinksSelectedEventData {
  selected_links: SelectedLink[];
}

export interface TokenEventData {
  chunk: string;
}

export interface CompleteEventData {
  status: string;
  total_pages_crawled: number;
  elapsed_seconds: number;
  company_name?: string;
}

export interface ErrorEventData {
  error: string;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}
