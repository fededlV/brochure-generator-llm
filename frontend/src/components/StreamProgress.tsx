import React, { useRef, useEffect } from 'react';
import {
  CheckCircle,
  Loader2,
  ExternalLink,
  Terminal,
  Sparkles,
  Link2,
} from 'lucide-react';
import { PipelineStep, SelectedLink, LogEntry } from '../types';

interface StreamProgressProps {
  currentStep: PipelineStep;
  progressPercent: number;
  statusMessage: string;
  selectedLinks: SelectedLink[];
  logs: LogEntry[];
}

const PIPELINE_STAGES: { id: PipelineStep; label: string }[] = [
  { id: 'crawling_landing', label: 'Crawl Landing' },
  { id: 'analyzing_links', label: 'AI Link Filtering' },
  { id: 'crawling_subpages', label: 'Crawl Subpages' },
  { id: 'generating_brochure', label: 'Synthesize Brochure' },
];

export const StreamProgress: React.FC<StreamProgressProps> = ({
  currentStep,
  progressPercent,
  statusMessage,
  selectedLinks,
  logs,
}) => {
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const getStepStatus = (stageId: PipelineStep) => {
    const stageOrder: PipelineStep[] = [
      'validating',
      'crawling_landing',
      'analyzing_links',
      'crawling_subpages',
      'generating_brochure',
      'completed',
    ];
    const currentIndex = stageOrder.indexOf(currentStep);
    const stageIndex = stageOrder.indexOf(stageId);

    if (currentStep === 'completed') return 'completed';
    if (currentIndex > stageIndex) return 'completed';
    if (currentIndex === stageIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 p-6 space-y-6 transition-all">
      {/* Header and Progress Bar */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 text-brand-600 animate-spin" />
            <span className="text-sm font-semibold text-slate-800">
              {statusMessage || 'Processing...'}
            </span>
          </div>
          <span className="text-xs font-bold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-full border border-brand-200">
            {progressPercent}%
          </span>
        </div>

        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
          <div
            className="bg-gradient-to-r from-brand-600 to-indigo-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Stepper visual */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        {PIPELINE_STAGES.map((stage) => {
          const status = getStepStatus(stage.id);
          return (
            <div
              key={stage.id}
              className={`p-2.5 rounded-xl border flex items-center space-x-2 transition-all ${
                status === 'completed'
                  ? 'border-emerald-200 bg-emerald-50/50 text-emerald-800'
                  : status === 'active'
                  ? 'border-brand-500 bg-brand-50/50 text-brand-900 ring-2 ring-brand-500/10 font-semibold'
                  : 'border-slate-200 bg-slate-50 text-slate-400'
              }`}
            >
              {status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : status === 'active' ? (
                <Loader2 className="w-4 h-4 text-brand-600 animate-spin shrink-0" />
              ) : (
                <div className="w-2 h-2 rounded-full bg-slate-300 ml-1 mr-1 shrink-0" />
              )}
              <span className="truncate">{stage.label}</span>
            </div>
          );
        })}
      </div>

      {/* Selected Links by AI Callout */}
      {selectedLinks.length > 0 && (
        <div className="rounded-xl border border-indigo-100 bg-indigo-50/30 p-4 space-y-2.5">
          <div className="flex items-center space-x-2 text-xs font-bold text-indigo-900">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>Gemini selected {selectedLinks.length} high-value pages:</span>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {selectedLinks.map((link, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between p-2.5 rounded-lg bg-white border border-indigo-100 text-xs shadow-2xs"
              >
                <div className="flex items-start space-x-2 truncate pr-2">
                  <Link2 className="w-3.5 h-3.5 text-indigo-500 shrink-0 mt-0.5" />
                  <div className="truncate">
                    <span className="font-semibold text-slate-800 block truncate">
                      {link.url}
                    </span>
                    <span className="text-slate-500 text-[11px] block mt-0.5">
                      {link.reason}
                    </span>
                  </div>
                </div>
                <a
                  href={link.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-600 hover:text-indigo-800 shrink-0 p-1"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Console Log */}
      <div className="activity-log rounded-xl bg-slate-900 text-slate-200 text-xs font-mono p-3 border border-slate-800">
        <div className="flex items-center space-x-1.5 pb-2 border-b border-slate-800 text-[11px] text-slate-400">
          <Terminal className="w-3.5 h-3.5" />
          <span>Real-time Execution Stream</span>
        </div>
        <div
          ref={logContainerRef}
          className="mt-2 space-y-1 max-h-36 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700"
        >
          {logs.map((log, i) => (
            <div key={i} className="flex space-x-2 text-[11px] leading-relaxed">
              <span className="text-slate-500 shrink-0">{log.timestamp}</span>
              <span
                className={
                  log.type === 'success'
                    ? 'text-emerald-400'
                    : log.type === 'error'
                    ? 'text-rose-400'
                    : log.type === 'warning'
                    ? 'text-amber-400'
                    : 'text-slate-300'
                }
              >
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
