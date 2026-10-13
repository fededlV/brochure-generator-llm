import React, { useState } from 'react';
import { Copy, Check, Download, Printer } from 'lucide-react';

interface ExportActionsProps {
  markdownContent: string;
  companyName?: string;
}

export const ExportActions: React.FC<ExportActionsProps> = ({
  markdownContent,
  companyName = 'Company',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdownContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard', err);
    }
  };

  const handleDownloadMarkdown = () => {
    const filename = `${companyName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-brochure.md`;
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePrintPdf = () => {
    window.print();
  };

  const wordCount = markdownContent.trim().split(/\s+/).filter(Boolean).length;
  const readingTimeMinutes = Math.max(1, Math.round(wordCount / 200));

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-slate-50 border-b border-slate-200 text-xs no-print">
      <div className="flex items-center space-x-3 text-slate-500 font-medium">
        <span>{wordCount} words</span>
        <span>•</span>
        <span>~{readingTimeMinutes} min read</span>
      </div>

      <div className="flex items-center space-x-2">
        {/* Copy Button */}
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 hover:text-slate-900 text-slate-700 transition font-medium cursor-pointer shadow-2xs"
          title="Copy Markdown"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Markdown</span>
            </>
          )}
        </button>

        {/* Download .md */}
        <button
          type="button"
          onClick={handleDownloadMarkdown}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 hover:text-slate-900 text-slate-700 transition font-medium cursor-pointer shadow-2xs"
          title="Download as Markdown file"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download .md</span>
        </button>

        {/* Print / Save PDF */}
        <button
          type="button"
          onClick={handlePrintPdf}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-50 border border-brand-200 hover:bg-brand-100 text-brand-700 transition font-medium cursor-pointer shadow-2xs"
          title="Print or Save as PDF"
        >
          <Printer className="w-3.5 h-3.5" />
          <span className="font-semibold">Print / Save as PDF</span>
        </button>
      </div>
    </div>
  );
};
