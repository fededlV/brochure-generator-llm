import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen } from 'lucide-react';
import { ExportActions } from './ExportActions';

interface BrochureViewerProps {
  content: string;
  isStreaming: boolean;
  companyName?: string;
}

export const BrochureViewer: React.FC<BrochureViewerProps> = ({
  content,
  isStreaming,
  companyName,
}) => {
  if (!content && !isStreaming) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 p-12 text-center flex flex-col items-center justify-center min-h-[420px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 mb-4 shadow-2xs">
          <BookOpen className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-slate-800 mb-1">
          No brochure generated yet
        </h3>
        <p className="text-xs text-slate-500 max-w-sm">
          Enter any corporate website URL on the left and select your target audience to produce a publication-ready marketing brochure.
        </p>
      </div>
    );
  }

  return (
    <div className="brochure-container bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden transition-all">
      {content && (
        <ExportActions markdownContent={content} companyName={companyName} />
      )}

      <div className="p-6 sm:p-10 max-w-none">
        <article className="prose prose-slate max-w-none prose-headings:font-bold prose-h1:text-2xl sm:prose-h1:text-3xl prose-h1:tracking-tight prose-h1:text-slate-900 prose-h2:text-xl prose-h2:text-slate-800 prose-h2:border-b prose-h2:border-slate-100 prose-h2:pb-2 prose-h2:mt-8 prose-h3:text-lg prose-h3:text-slate-800 prose-p:text-slate-600 prose-p:leading-relaxed prose-li:text-slate-600 prose-strong:text-slate-900 prose-blockquote:border-l-4 prose-blockquote:border-brand-500 prose-blockquote:bg-brand-50/30 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:text-slate-700">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>

          {isStreaming && (
            <span className="inline-block w-2.5 h-5 ml-1 bg-brand-600 animate-pulse align-middle" />
          )}
        </article>
      </div>
    </div>
  );
};
