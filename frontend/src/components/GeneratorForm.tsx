import React, { useState } from 'react';
import {
  Globe,
  Users,
  Briefcase,
  TrendingUp,
  Sparkles,
  Layers,
  StopCircle,
  ArrowRight,
  Sliders
} from 'lucide-react';
import { Audience, Tone, GenerationRequest } from '../types';

interface GeneratorFormProps {
  onSubmit: (request: GenerationRequest) => void;
  onStop: () => void;
  isGenerating: boolean;
}

const EXAMPLE_URLS = [
  { label: 'Hugging Face', url: 'https://huggingface.co' },
  { label: 'YPF', url: 'https://ypf.com' },
  { label: 'Supabase', url: 'https://supabase.com' },
];

export const GeneratorForm: React.FC<GeneratorFormProps> = ({
  onSubmit,
  onStop,
  isGenerating,
}) => {
  const [url, setUrl] = useState('');
  const [audience, setAudience] = useState<Audience>('prospects');
  const [tone, setTone] = useState<Tone>('professional');
  const [maxSubpages, setMaxSubpages] = useState(3);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || isGenerating) return;
    onSubmit({
      url: url.trim(),
      audience,
      tone,
      max_subpages: maxSubpages,
    });
  };

  const audienceOptions: { id: Audience; title: string; desc: string; icon: any }[] = [
    {
      id: 'prospects',
      title: 'Prospects & Clients',
      desc: 'Value proposition, ROI, & product offerings',
      icon: Users,
    },
    {
      id: 'investors',
      title: 'Investors & Analysts',
      desc: 'Market moat, business model, & traction',
      icon: TrendingUp,
    },
    {
      id: 'candidates',
      title: 'Job Candidates',
      desc: 'Culture, vision, tech stack, & mission',
      icon: Briefcase,
    },
    {
      id: 'general',
      title: 'General Profile',
      desc: 'Balanced, multi-purpose company overview',
      icon: Layers,
    },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 p-6 sm:p-8 transition-all">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="company-url" className="block text-sm font-semibold text-slate-800 mb-2">
            Company Website URL
          </label>
          <div className="relative rounded-xl shadow-xs">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Globe className="w-5 h-5" />
            </div>
            <input
              id="company-url"
              type="text"
              required
              disabled={isGenerating}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="e.g. https://huggingface.co"
              className="block w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-900 placeholder:text-slate-400 focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 text-sm transition-all outline-hidden disabled:opacity-60"
            />
          </div>

          {/* Quick Examples */}
          <div className="mt-2.5 flex items-center flex-wrap gap-2 text-xs text-slate-500">
            <span className="font-medium text-slate-400">Try an example:</span>
            {EXAMPLE_URLS.map((ex) => (
              <button
                key={ex.url}
                type="button"
                disabled={isGenerating}
                onClick={() => setUrl(ex.url)}
                className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200/80 text-slate-700 transition font-medium text-[11px]"
              >
                {ex.label}
              </button>
            ))}
          </div>
        </div>

        {/* Target Audience Selector */}
        <div>
          <label className="block text-sm font-semibold text-slate-800 mb-2">
            Target Audience
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {audienceOptions.map((opt) => {
              const Icon = opt.icon;
              const isSelected = audience === opt.id;
              return (
                <button
                  key={opt.id}
                  type="button"
                  disabled={isGenerating}
                  onClick={() => setAudience(opt.id)}
                  className={`flex items-start p-3.5 rounded-xl border text-left transition-all ${
                    isSelected
                      ? 'border-brand-500 bg-brand-50/50 ring-2 ring-brand-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div
                    className={`p-2 rounded-lg mr-3 shrink-0 ${
                      isSelected
                        ? 'bg-brand-500 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-slate-800">{opt.title}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{opt.desc}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <div className="pt-1">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
          >
            <Sliders className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            {showAdvanced ? 'Hide advanced settings' : 'Show advanced settings (tone & depth)'}
          </button>

          {showAdvanced && (
            <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-4 animate-in fade-in-50 duration-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Tone */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Brochure Tone
                  </label>
                  <select
                    disabled={isGenerating}
                    value={tone}
                    onChange={(e) => setTone(e.target.value as Tone)}
                    className="w-full text-xs font-medium bg-white border border-slate-200 rounded-lg p-2.5 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-hidden"
                  >
                    <option value="professional">Professional & Corporate</option>
                    <option value="energetic">Energetic & Startup-focused</option>
                    <option value="minimalist">Minimalist Executive Brief</option>
                  </select>
                </div>

                {/* Subpage Depth */}
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      Subpage Crawl Depth
                    </label>
                    <span className="text-xs font-bold text-brand-600">
                      {maxSubpages} {maxSubpages === 1 ? 'page' : 'pages'}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    disabled={isGenerating}
                    value={maxSubpages}
                    onChange={(e) => setMaxSubpages(parseInt(e.target.value, 10))}
                    className="w-full accent-brand-600 h-2 bg-slate-200 rounded-lg cursor-pointer"
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Number of intelligent secondary links Gemini will crawl
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit or Stop Actions */}
        <div className="pt-2">
          {isGenerating ? (
            <button
              type="button"
              onClick={onStop}
              className="w-full py-3.5 px-6 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold flex items-center justify-center space-x-2 shadow-md shadow-rose-600/20 transition-all cursor-pointer"
            >
              <StopCircle className="w-5 h-5 animate-pulse" />
              <span>Cancel Generation</span>
            </button>
          ) : (
            <button
              type="submit"
              disabled={!url.trim()}
              className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-brand-600/25 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <Sparkles className="w-5 h-5 transition-transform group-hover:scale-110" />
              <span>Generate Company Brochure</span>
              <ArrowRight className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
