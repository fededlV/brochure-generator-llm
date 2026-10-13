import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { GeneratorForm } from './components/GeneratorForm';
import { StreamProgress } from './components/StreamProgress';
import { BrochureViewer } from './components/BrochureViewer';
import {
  PipelineStep,
  SelectedLink,
  LogEntry,
  GenerationRequest,
} from './types';
import { checkBackendHealth, streamBrochureGeneration } from './services/api';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [backendReady, setBackendReady] = useState(false);
  const [modelName, setModelName] = useState('Gemini 2.5 Flash');
  const [isGenerating, setIsGenerating] = useState(false);

  // Streaming State
  const [currentStep, setCurrentStep] = useState<PipelineStep>('idle');
  const [progressPercent, setProgressPercent] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [selectedLinks, setSelectedLinks] = useState<SelectedLink[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [brochureMarkdown, setBrochureMarkdown] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Initial health check
    checkBackendHealth().then((res) => {
      if (res.status === 'ok') {
        setBackendReady(true);
        if (res.model) setModelName(res.model);
      }
    });
  }, []);

  const addLog = (message: string, type: LogEntry['type'] = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, { timestamp, message, type }]);
  };

  const handleStartGeneration = async (request: GenerationRequest) => {
    // Reset state for new run
    setErrorBanner(null);
    setIsGenerating(true);
    setCurrentStep('validating');
    setProgressPercent(5);
    setStatusMessage('Initiating research pipeline...');
    setSelectedLinks([]);
    setLogs([]);
    setBrochureMarkdown('');
    setCompanyName('');

    addLog(`Initiating research for: ${request.url}`, 'info');
    addLog(`Audience: ${request.audience} | Tone: ${request.tone} | Max subpages: ${request.max_subpages}`, 'info');

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await streamBrochureGeneration(
        request,
        {
          onStatus: (data) => {
            setCurrentStep(data.step);
            setProgressPercent(data.progress);
            setStatusMessage(data.message);
            addLog(data.message, 'info');
          },
          onLinksSelected: (data) => {
            setSelectedLinks(data.selected_links);
            addLog(`Gemini filtered ${data.selected_links.length} relevant subpages.`, 'success');
          },
          onToken: (data) => {
            setBrochureMarkdown((prev) => prev + data.chunk);
          },
          onComplete: (data) => {
            setCurrentStep('completed');
            setProgressPercent(100);
            setStatusMessage(`Completed in ${data.elapsed_seconds}s!`);
            if (data.company_name) setCompanyName(data.company_name);
            addLog(`Brochure generated successfully in ${data.elapsed_seconds}s across ${data.total_pages_crawled} pages!`, 'success');
            setIsGenerating(false);
          },
          onError: (data) => {
            setCurrentStep('error');
            setErrorBanner(data.error);
            addLog(`Error: ${data.error}`, 'error');
            setIsGenerating(false);
          },
        },
        controller.signal
      );
    } catch (err: any) {
      setErrorBanner(err.message || 'Stream processing failed');
      addLog(`Unexpected error: ${err.message}`, 'error');
      setIsGenerating(false);
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsGenerating(false);
    addLog('Generation cancelled by user.', 'warning');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header backendReady={backendReady} modelName={modelName} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full grow">
        {/* Error Alert Banner */}
        {errorBanner && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-3 shadow-xs">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="grow">
              <span className="font-bold">Generation Error: </span>
              <span>{errorBanner}</span>
            </div>
            <button
              onClick={() => setErrorBanner(null)}
              className="text-rose-500 hover:text-rose-700 font-bold px-1.5"
            >
              ×
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Form & Live Progress */}
          <div className="lg:col-span-5 space-y-6 no-print">
            <GeneratorForm
              onSubmit={handleStartGeneration}
              onStop={handleStopGeneration}
              isGenerating={isGenerating}
            />

            {(isGenerating || logs.length > 0) && (
              <StreamProgress
                currentStep={currentStep}
                progressPercent={progressPercent}
                statusMessage={statusMessage}
                selectedLinks={selectedLinks}
                logs={logs}
              />
            )}
          </div>

          {/* Right Column: Live Markdown Brochure Preview & Export */}
          <div className="lg:col-span-7">
            <BrochureViewer
              content={brochureMarkdown}
              isStreaming={isGenerating && currentStep === 'generating_brochure'}
              companyName={companyName}
            />
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 no-print">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI Company Brochure Generator — Built with Spec-Driven Development (SDD)</span>
          <span className="text-slate-400">FastAPI • Google GenAI • React • Tailwind</span>
        </div>
      </footer>
    </div>
  );
};
