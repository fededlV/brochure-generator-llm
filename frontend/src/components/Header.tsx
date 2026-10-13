import React from 'react';
import { Sparkles, Globe2, CheckCircle2, AlertCircle } from 'lucide-react';

interface HeaderProps {
  backendReady: boolean;
  modelName: string;
}

export const Header: React.FC<HeaderProps> = ({ backendReady, modelName }) => {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 ring-1 ring-white/30">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-extrabold text-slate-900 text-lg tracking-tight">
                BrochureAI
              </h1>
              <span className="text-[11px] font-semibold bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full border border-brand-200">
                SDD Architecture
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Intelligent multi-page web research & marketing brochure generator
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200 text-slate-700">
            <Globe2 className="w-3.5 h-3.5 text-slate-500" />
            <span className="hidden md:inline text-slate-500">Model:</span>
            <span className="font-semibold text-slate-800">{modelName || 'Gemini 2.5 Flash'}</span>
            {backendReady ? (
              <span className="flex items-center text-emerald-600 font-medium pl-1">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Ready
              </span>
            ) : (
              <span className="flex items-center text-amber-600 font-medium pl-1">
                <AlertCircle className="w-3.5 h-3.5 mr-1" /> Connecting
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
