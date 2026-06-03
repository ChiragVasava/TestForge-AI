"use client";

import React, { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { 
  ArrowLeft,
  Terminal, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  HelpCircle,
  Activity,
  Layers,
  FileCode,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  Clock,
  ClipboardList
} from "lucide-react";

interface TestCase {
  name: string;
  classname: string;
  time: number;
  status: "passed" | "failed" | "error" | "skipped";
  failure_message: string | null;
}

interface CoverageFileInfo {
  percent_covered: number;
  missing_lines: number[];
  executed_lines: number[];
  num_statements: number;
}

interface CoverageData {
  percentage: number;
  files: Record<string, CoverageFileInfo>;
  error?: string;
}

interface RunReportData {
  id: number;
  project_id: number;
  status: string;
  passed_count: number;
  failed_count: number;
  coverage_percentage: number;
  stdout_logs: string;
  coverage_report: string; // JSON string
  created_at: string;
}

export default function RunReportPage({ params }: { params: Promise<{ id: string; run_id: string }> }) {
  const resolvedParams = use(params);
  const projectId = resolvedParams.id;
  const runId = resolvedParams.run_id;
  const router = useRouter();

  // State
  const [project, setProject] = useState<any>(null);
  const [report, setReport] = useState<RunReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"cases" | "coverage" | "logs">("cases");
  const [expandedCases, setExpandedCases] = useState<Record<number, boolean>>({});
  const [copySuccess, setCopySuccess] = useState(false);

  // Parsed coverage & test cases
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [coverage, setCoverage] = useState<CoverageData | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const loadReport = async () => {
      try {
        const proj = await apiRequest(`/projects/${projectId}`);
        setProject(proj);

        const data: RunReportData = await apiRequest(`/tests/${projectId}/runs/${runId}`);
        setReport(data);

        // Parse combined coverage report
        if (data.coverage_report) {
          try {
            const parsed = JSON.parse(data.coverage_report);
            setCoverage(parsed.coverage || null);
            setTestCases(parsed.test_cases || []);
          } catch (e) {
            console.error("Failed to parse coverage report JSON", e);
          }
        }
      } catch (err: any) {
        console.error("Error loading run report:", err);
      } finally {
        setLoading(false);
      }
    };

    loadReport();
  }, [projectId, runId, router]);

  const toggleExpandCase = (index: number) => {
    setExpandedCases(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleCopyLogs = () => {
    if (!report?.stdout_logs) return;
    navigator.clipboard.writeText(report.stdout_logs);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="flex flex-col items-center gap-4">
          <span className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
          <p className="text-gray-400 text-sm animate-pulse">Parsing PyTest report logs...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 text-white p-6 text-center">
        <div className="max-w-xs space-y-4">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <h3 className="text-lg font-bold">Report Not Found</h3>
          <p className="text-gray-400 text-sm">The requested test execution run logs do not exist or were deleted.</p>
          <button
            onClick={() => router.push(`/projects/${projectId}`)}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold hover:bg-indigo-500 transition-all cursor-pointer"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const totalTests = report.passed_count + report.failed_count;
  const passRate = totalTests > 0 ? Math.round((report.passed_count / totalTests) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col h-screen overflow-hidden">
      {/* Navbar header */}
      <header className="border-b border-gray-900 bg-gray-950/80 backdrop-blur-md px-6 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(`/projects/${projectId}`)}
            className="p-2 rounded-lg border border-gray-900 hover:bg-gray-900 text-gray-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 uppercase tracking-widest">Test Run Report</span>
              <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                report.status === "passed" ? "badge-pass" : "badge-fail"
              }`}>
                {report.status}
              </span>
            </div>
            <h1 className="text-lg font-bold">{project?.name} - Run #{report.id}</h1>
          </div>
        </div>

        <div className="text-xs text-gray-500">
          Executed {new Date(report.created_at).toLocaleString()}
        </div>
      </header>

      {/* Main split dashboard panels */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Column: KPI metrics summary */}
        <aside className="w-80 border-r border-gray-900 bg-gray-950 p-6 flex flex-col gap-6 shrink-0 overflow-y-auto">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400">Run Summary</h2>
            <p className="text-xs text-gray-500 mt-1">High level execution results and coverage analytics.</p>
          </div>

          <div className="space-y-4">
            {/* Pass Rate Metric */}
            <div className="glass-card rounded-xl p-4.5 border border-gray-900 flex flex-col gap-1.5 relative overflow-hidden">
              <span className="text-[10px] uppercase font-bold text-gray-400">Success Rate</span>
              <div className="flex items-baseline gap-2">
                <span className={`text-3xl font-black ${report.status === "passed" ? "text-emerald-400" : "text-red-400"}`}>
                  {passRate}%
                </span>
                <span className="text-xs text-gray-500">pass rate</span>
              </div>
              <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden mt-1.5">
                <div 
                  className={`h-full rounded-full ${report.status === "passed" ? "bg-emerald-500" : "bg-red-500"}`}
                  style={{ width: `${passRate}%` }}
                />
              </div>
            </div>

            {/* Coverage Metric */}
            <div className="glass-card rounded-xl p-4.5 border border-gray-900 flex flex-col gap-1.5 relative overflow-hidden">
              <span className="text-[10px] uppercase font-bold text-gray-400">Total Code Coverage</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-cyan-400">
                  {report.coverage_percentage}%
                </span>
                <span className="text-xs text-gray-500">covered lines</span>
              </div>
              <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden mt-1.5">
                <div 
                  className="h-full rounded-full bg-cyan-500"
                  style={{ width: `${report.coverage_percentage}%` }}
                />
              </div>
            </div>

            {/* Test Count Card */}
            <div className="glass-card rounded-xl p-4.5 border border-gray-900 grid grid-cols-2 gap-4">
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 block">Passed</span>
                <span className="text-xl font-bold text-emerald-400">{report.passed_count}</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 block">Failed</span>
                <span className="text-xl font-bold text-red-400">{report.failed_count}</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Center/Right Section: Interactive Tabbed Workspace */}
        <section className="flex-1 flex flex-col overflow-hidden bg-gray-950/50">
          
          {/* Tab Toolbar Selector */}
          <div className="px-6 py-2.5 border-b border-gray-900 flex items-center justify-between shrink-0 bg-gray-950">
            <div className="flex gap-1.5">
              <button
                onClick={() => setActiveTab("cases")}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === "cases"
                    ? "bg-gray-900 text-white border border-gray-800"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <ClipboardList className="h-3.5 w-3.5" />
                <span>Test Cases ({testCases.length})</span>
              </button>
              <button
                onClick={() => setActiveTab("coverage")}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === "coverage"
                    ? "bg-gray-900 text-white border border-gray-800"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <Activity className="h-3.5 w-3.5" />
                <span>Coverage breakdown</span>
              </button>
              <button
                onClick={() => setActiveTab("logs")}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === "logs"
                    ? "bg-gray-900 text-white border border-gray-800"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <Terminal className="h-3.5 w-3.5" />
                <span>Terminal Outputs</span>
              </button>
            </div>

            {activeTab === "logs" && (
              <button
                onClick={handleCopyLogs}
                className="flex items-center gap-2 rounded-lg bg-gray-900 border border-gray-800 hover:border-gray-700 px-3.5 py-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-all cursor-pointer"
              >
                {copySuccess ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copySuccess ? "Copied!" : "Copy Console Log"}</span>
              </button>
            )}
          </div>

          {/* Dynamic Tab Body */}
          <div className="flex-1 overflow-y-auto p-6">
            
            {/* Tab 1: Test Cases checklist */}
            {activeTab === "cases" && (
              <div className="space-y-3.5">
                {testCases.length === 0 ? (
                  <div className="text-center py-16 text-gray-500">
                    <ClipboardList className="h-10 w-10 text-gray-700 mx-auto mb-2" />
                    <p className="text-sm italic">No test cases executed. Pytest likely failed compilation or failed to discover tests.</p>
                  </div>
                ) : (
                  testCases.map((tc, idx) => {
                    const isExpanded = expandedCases[idx] || false;
                    return (
                      <div 
                        key={idx} 
                        className={`glass-card rounded-xl border transition-all overflow-hidden ${
                          tc.status === "passed" ? "border-gray-900" : "border-red-500/20"
                        }`}
                      >
                        {/* Summary Header */}
                        <div 
                          onClick={() => (tc.status !== "passed" ? toggleExpandCase(idx) : null)}
                          className={`p-4 flex items-center justify-between text-xs transition-colors select-none ${
                            tc.status !== "passed" ? "cursor-pointer hover:bg-gray-900/20" : ""
                          }`}
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            {tc.status === "passed" ? (
                              <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400 shrink-0" />
                            ) : tc.status === "failed" ? (
                              <XCircle className="h-4.5 w-4.5 text-red-400 shrink-0" />
                            ) : (
                              <AlertCircle className="h-4.5 w-4.5 text-amber-500 shrink-0" />
                            )}
                            <div className="truncate">
                              <p className="font-bold text-white truncate">{tc.name}</p>
                              <p className="text-[10px] text-gray-500 mt-0.5 truncate">{tc.classname}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-3 shrink-0 ml-4">
                            <span className="text-[10px] text-gray-500 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {tc.time.toFixed(3)}s
                            </span>
                            <span className={`text-[9px] uppercase font-bold px-2 py-0.5 rounded ${
                              tc.status === "passed" 
                                ? "badge-pass" 
                                : tc.status === "failed" 
                                ? "badge-fail" 
                                : "badge-running"
                            }`}>
                              {tc.status}
                            </span>
                            {tc.status !== "passed" && (
                              <div>
                                {isExpanded ? <ChevronDown className="h-4 w-4 text-gray-500" /> : <ChevronRight className="h-4 w-4 text-gray-500" />}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Expanded details (failure stack trace) */}
                        {isExpanded && tc.failure_message && (
                          <div className="border-t border-red-500/20 bg-red-950/10 p-4">
                            <pre className="text-[10px] font-mono text-red-300 leading-relaxed overflow-x-auto whitespace-pre-wrap select-text">
                              <code>{tc.failure_message}</code>
                            </pre>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            )}

            {/* Tab 2: Coverage detailed breakdown */}
            {activeTab === "coverage" && (
              <div className="space-y-6">
                {!coverage || Object.keys(coverage.files).length === 0 ? (
                  <div className="text-center py-16 text-gray-500">
                    <Activity className="h-10 w-10 text-gray-700 mx-auto mb-2" />
                    <p className="text-sm italic">Coverage details not available.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(coverage.files).map(([filename, fileinfo]) => {
                      const covPct = fileinfo.percent_covered;
                      const colorClass = covPct >= 80 
                        ? "bg-emerald-500" 
                        : covPct >= 50 
                        ? "bg-amber-500" 
                        : "bg-red-500";
                        
                      return (
                        <div key={filename} className="glass-card rounded-xl p-5 border border-gray-900 space-y-4">
                          {/* File header metrics */}
                          <div className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-2.5 min-w-0">
                              <FileCode className="h-4.5 w-4.5 text-cyan-400 shrink-0" />
                              <span className="text-xs font-bold text-white truncate">{filename}</span>
                            </div>
                            <div className="flex items-center gap-4 shrink-0 text-xs">
                              <span className="text-gray-400">
                                Statements: <strong className="text-white">{fileinfo.num_statements}</strong>
                              </span>
                              <span className={`font-bold px-2 py-0.5 rounded ${
                                covPct >= 80 
                                  ? "badge-pass" 
                                  : covPct >= 50 
                                  ? "badge-running" 
                                  : "badge-fail"
                              }`}>
                                {covPct}% Covered
                              </span>
                            </div>
                          </div>

                          {/* Progress bar */}
                          <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${covPct}%` }} />
                          </div>

                          {/* Missing lines info */}
                          {fileinfo.missing_lines.length > 0 ? (
                            <div className="text-[10px] text-gray-500 flex gap-2 items-center flex-wrap">
                              <span className="font-semibold text-gray-400">Missing Lines:</span>
                              <div className="flex gap-1 flex-wrap">
                                {fileinfo.missing_lines.map((line) => (
                                  <span key={line} className="px-1.5 py-0.5 rounded bg-gray-900 border border-gray-800 text-gray-400">
                                    {line}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <p className="text-[10px] text-emerald-400 font-semibold">✓ 100% test coverage achieved for this module.</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* Tab 3: Terminal Console Log */}
            {activeTab === "logs" && (
              <div className="h-full flex flex-col">
                <pre className="flex-1 bg-black rounded-xl p-5 text-[10px] font-mono text-emerald-400 leading-relaxed overflow-y-auto whitespace-pre select-text border border-gray-950 shadow-inner max-h-[500px]">
                  <code>{report.stdout_logs || "No console outputs captured."}</code>
                </pre>
              </div>
            )}

          </div>
        </section>

      </div>
    </div>
  );
}
