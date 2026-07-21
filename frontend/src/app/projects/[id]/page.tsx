"use client";

import React, { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { 
  ArrowLeft,
  FileCode, 
  Upload, 
  Terminal, 
  Sparkles, 
  Play, 
  Save, 
  Copy, 
  Check, 
  History, 
  FileText, 
  Code,
  AlertCircle,
  HelpCircle,
  Clock,
  Layers,
  Plus,
  Download,
  Database,
  FileSpreadsheet,
  Trash2
} from "lucide-react";

interface FileItem {
  id: number;
  filename: string;
  created_at: string;
}

interface ArgMeta {
  name: string;
  annotation: string | null;
  has_default: boolean;
  default_value?: string;
}

interface MethodMeta {
  name: string;
  is_async: boolean;
  args: ArgMeta[];
  return_type: string | null;
  docstring: string | null;
}

interface ClassMeta {
  name: string;
  docstring: string | null;
  methods: MethodMeta[];
}

interface FunctionMeta {
  name: string;
  is_async: boolean;
  args: ArgMeta[];
  return_type: string | null;
  docstring: string | null;
}

interface FileAnalysis {
  classes: ClassMeta[];
  functions: FunctionMeta[];
  imports: string[];
}

interface TestRun {
  id: number;
  status: string;
  passed_count: number;
  failed_count: number;
  coverage_percentage: number;
  created_at: string;
}

interface GeneratedTest {
  id: number;
  project_id: number;
  filename: string;
  content: string;
}

interface AISuggestion {
  title: string;
  explanation: string;
  test_code: string;
}

export default function ProjectWorkspace({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const projectId = resolvedParams.id;
  const router = useRouter();

  // Mode Selection: 'unit' (Unit & Code Testing) | 'qa' (QA Automation & Test Cases)
  const [workspaceMode, setWorkspaceMode] = useState<"unit" | "qa">("unit");

  // State (Unit & Code Testing)
  const [project, setProject] = useState<any>(null);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [fileContent, setFileContent] = useState("");
  const [analysis, setAnalysis] = useState<FileAnalysis | null>(null);
  const [selectedElement, setSelectedElement] = useState<{ name: string; type: "class" | "function" } | null>(null);
  const [activeTab, setActiveTab] = useState<"source" | "tests">("source");
  const [testContent, setTestContent] = useState("");
  const [testFilename, setTestFilename] = useState("");
  const [testsList, setTestsList] = useState<GeneratedTest[]>([]);
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [runLoading, setRunLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestion[]>([]);
  const [aiError, setAiError] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [copySuccessMap, setCopySuccessMap] = useState<Record<number | string, boolean>>({});
  const [testSuccessMessage, setTestSuccessMessage] = useState("");

  // State (QA Automation Mode)
  const [testCases, setTestCases] = useState<any[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<any | null>(null);
  const [testDataList, setTestDataList] = useState<any[]>([]);
  
  // Test Case form states
  const [newTcTitle, setNewTcTitle] = useState("");
  const [newTcDesc, setNewTcDesc] = useState("");
  const [newTcSteps, setNewTcSteps] = useState("");
  const [newTcExpected, setNewTcExpected] = useState("");
  const [newTcData, setNewTcData] = useState("");
  const [showTcModal, setShowTcModal] = useState(false);
  const [tcSubmitLoading, setTcSubmitLoading] = useState(false);
  
  // Test Data form states
  const [newValKey, setNewValKey] = useState("");
  const [newValValue, setNewValValue] = useState("");
  const [newValDesc, setNewValDesc] = useState("");
  const [valSubmitLoading, setValSubmitLoading] = useState(false);
  
  // Automation script states
  const [generatedScript, setGeneratedScript] = useState("");
  const [scriptLoading, setScriptLoading] = useState(false);
  const [csvImportLoading, setCsvImportLoading] = useState(false);

  // Load project details
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const loadProject = async () => {
      try {
        const proj = await apiRequest(`/projects/${projectId}`);
        setProject(proj);
        
        const fileList = await apiRequest(`/projects/${projectId}/files`);
        setFiles(fileList);
        
        const testList = await apiRequest(`/tests/${projectId}/generated`);
        setTestsList(testList);
        
        const runList = await apiRequest(`/tests/${projectId}/runs`);
        setRuns(runList);

        const tcList = await apiRequest(`/testcases/${projectId}`);
        setTestCases(tcList);

        const tdList = await apiRequest(`/testcases/${projectId}/testdata`);
        setTestDataList(tdList);

        if (fileList.length > 0) {
          handleSelectFile(fileList[0]);
        }
      } catch (err: any) {
        console.error("Workspace load error:", err);
      }
    };

    loadProject();
  }, [projectId, router]);

  const handleSelectFile = async (fileItem: FileItem) => {
    setSelectedFile(fileItem);
    setSelectedElement(null);
    setAiSuggestions([]);
    setAiError("");
    
    try {
      const data = await apiRequest(`/projects/${projectId}/files/${fileItem.id}/content`);
      setFileContent(data.content);
      
      const parsed = await apiRequest(`/projects/${projectId}/upload`, {
        method: "POST",
        body: (() => {
          const form = new FormData();
          const blob = new Blob([data.content], { type: "text/plain" });
          form.append("file", blob, fileItem.filename);
          return form;
        })(),
      });
      setAnalysis(parsed.analysis);

      // Lookup if test template already exists
      const targetTestName = `test_${fileItem.filename.replace(".py", "")}.py`;
      const existingTest = testsList.find(t => t.filename === targetTestName);
      if (existingTest) {
        setTestContent(existingTest.content);
        setTestFilename(existingTest.filename);
      } else {
        // Generate new test template via API
        const generated = await apiRequest(`/tests/${projectId}/generate?filename=${fileItem.filename}`);
        setTestContent(generated.content);
        setTestFilename(generated.filename);
      }
    } catch (err: any) {
      console.error("Error reading file:", err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    setUploadLoading(true);
    const filesArray = Array.from(e.target.files);
    
    try {
      let lastResult = null;
      const uploadedFiles = [];

      for (const file of filesArray) {
        const form = new FormData();
        form.append("file", file);
        
        const result = await apiRequest(`/projects/${projectId}/upload`, {
          method: "POST",
          body: form,
        });
        lastResult = result;
        uploadedFiles.push(result.file);
      }

      // Update files list
      setFiles(prev => {
        const newFiles = [...prev];
        uploadedFiles.forEach(uploaded => {
          const idx = newFiles.findIndex(f => f.filename === uploaded.filename);
          if (idx !== -1) {
            newFiles[idx] = uploaded;
          } else {
            newFiles.push(uploaded);
          }
        });
        return newFiles;
      });

      if (lastResult) {
        setSelectedFile(lastResult.file);
        handleSelectFile(lastResult.file);
      }
    } catch (err: any) {
      alert(err.message || "Failed to upload file");
    } finally {
      setUploadLoading(false);
    }
  };

  const handleSelectElement = async (name: string, type: "class" | "function") => {
    setSelectedElement({ name, type });
    setAiLoading(true);
    setAiSuggestions([]);
    setAiError("");

    try {
      const data = await apiRequest("/ai/recommend", {
        method: "POST",
        body: JSON.stringify({
          file_id: selectedFile?.id,
          name,
          element_type: type,
        }),
      });

      if (data.error) {
        setAiError(data.error);
      } else {
        setAiSuggestions(data.suggestions || []);
      }
    } catch (err: any) {
      setAiError(err.message || "Failed to query Gemini AI recommendations");
    } finally {
      setAiLoading(false);
    }
  };

  const handleSaveTest = async () => {
    if (!testFilename) return;
    setSaveLoading(true);
    try {
      const saved = await apiRequest(`/tests/${projectId}/save`, {
        method: "POST",
        body: JSON.stringify({
          filename: testFilename,
          content: testContent,
          scanned_item_name: selectedFile?.filename
        }),
      });
      
      // Update tests list
      setTestsList(prev => {
        const exists = prev.some(t => t.id === saved.id);
        if (exists) {
          return prev.map(t => t.id === saved.id ? saved : t);
        }
        return [...prev, saved];
      });

      alert("PyTest template saved successfully!");
    } catch (err: any) {
      alert(err.message || "Failed to save test");
    } finally {
      setSaveLoading(false);
    }
  };

  const handleRunTests = async () => {
    if (testFilename) {
      try {
        await apiRequest(`/tests/${projectId}/save`, {
          method: "POST",
          body: JSON.stringify({
            filename: testFilename,
            content: testContent,
            scanned_item_name: selectedFile?.filename
          }),
        });
      } catch (err) {
        console.error("Auto save failed", err);
      }
    }

    setRunLoading(true);
    setTestSuccessMessage("");

    try {
      const result = await apiRequest(`/tests/${projectId}/run`, {
        method: "POST",
      });

      setRuns(prev => [result, ...prev]);
      setTestSuccessMessage(`PyTest Execution Finished: ${result.status.toUpperCase()}. Pass rate: ${result.passed_count}/${result.passed_count + result.failed_count}. Coverage: ${result.coverage_percentage}%`);
    } catch (err: any) {
      alert(err.message || "Failed to execute tests. Make sure you have saved test files first.");
    } finally {
      setRunLoading(false);
    }
  };

  const handleCopyCode = (code: string, id: number | string) => {
    navigator.clipboard.writeText(code);
    setCopySuccessMap(prev => ({ ...prev, [id]: true }));
    setTimeout(() => {
      setCopySuccessMap(prev => ({ ...prev, [id]: false }));
    }, 2000);
  };

  const handleAppendTest = (code: string) => {
    // 1. Identify all test function names in the incoming code
    const functionRegex = /def\s+(test_[a-zA-Z0-9_]+)\b/g;
    let match;
    const functionsInCode: string[] = [];
    while ((match = functionRegex.exec(code)) !== null) {
      functionsInCode.push(match[1]);
    }

    if (functionsInCode.length === 0) {
      // Fallback: If no test functions are found, just append the raw code
      setTestContent(prev => {
        const separator = prev.endsWith("\n\n") ? "" : prev.endsWith("\n") ? "\n" : "\n\n";
        return prev + separator + code.trim();
      });
      setActiveTab("tests");
      return;
    }

    // 2. Auto-rename duplicate functions against current testContent
    let modifiedCode = code;
    functionsInCode.forEach(funcName => {
      const escapedFuncName = funcName.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      const regexTestContent = new RegExp(`def\\s+${escapedFuncName}\\b`);
      
      if (regexTestContent.test(testContent)) {
        let suffix = 1;
        let newFuncName = `${funcName}_${suffix}`;
        while (
          new RegExp(`def\\s+${newFuncName}\\b`).test(testContent) ||
          new RegExp(`def\\s+${newFuncName}\\b`).test(modifiedCode)
        ) {
          suffix++;
          newFuncName = `${funcName}_${suffix}`;
        }
        
        // Replace `def funcName` with `def newFuncName` in the modifiedCode
        const replaceRegex = new RegExp(`def\\s+(${escapedFuncName})\\b`, 'g');
        modifiedCode = modifiedCode.replace(replaceRegex, `def ${newFuncName}`);
        console.log(`Auto-renamed duplicate test function ${funcName} to ${newFuncName}`);
      }
    });

    // 3. Clean the code to extract only the test block (filtering module level imports)
    const lines = modifiedCode.split("\n");
    const cleanedLines = lines.filter(line => {
      const trimmed = line.trim();
      return !trimmed.startsWith("import ") && !trimmed.startsWith("from ");
    });
    const cleanedCode = cleanedLines.join("\n").trim();

    if (!cleanedCode) return;

    // 4. Append to suite content
    setTestContent(prev => {
      const separator = prev.endsWith("\n\n") ? "" : prev.endsWith("\n") ? "\n" : "\n\n";
      return prev + separator + cleanedCode;
    });
    setActiveTab("tests");
  };

  // QA Automation Mode Logic
  const handleCreateTestCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTcTitle.trim() || !newTcSteps.trim() || !newTcExpected.trim()) {
      alert("Title, Steps, and Expected Result are required");
      return;
    }
    setTcSubmitLoading(true);
    try {
      const created = await apiRequest(`/testcases/${projectId}`, {
        method: "POST",
        body: JSON.stringify({
          title: newTcTitle,
          description: newTcDesc,
          steps: newTcSteps,
          expected_result: newTcExpected,
          test_data: newTcData
        })
      });
      setTestCases(prev => [...prev, created]);
      setShowTcModal(false);
      setNewTcTitle("");
      setNewTcDesc("");
      setNewTcSteps("");
      setNewTcExpected("");
      setNewTcData("");
      alert("Test Case created successfully!");
    } catch (err: any) {
      alert(err.message || "Failed to create test case");
    } finally {
      setTcSubmitLoading(false);
    }
  };

  const handleDeleteTestCase = async (tcId: number) => {
    if (!confirm("Are you sure you want to delete this test case?")) return;
    try {
      await apiRequest(`/testcases/${projectId}/${tcId}`, {
        method: "DELETE"
      });
      setTestCases(prev => prev.filter(t => t.id !== tcId));
      if (selectedTestCase?.id === tcId) {
        setSelectedTestCase(null);
        setGeneratedScript("");
      }
    } catch (err: any) {
      alert(err.message || "Failed to delete testcase");
    }
  };

  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setCsvImportLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await apiRequest(`/testcases/${projectId}/import`, {
        method: "POST",
        body: form
      });
      alert(res.message);
      const list = await apiRequest(`/testcases/${projectId}`);
      setTestCases(list);
    } catch (err: any) {
      alert(err.message || "Failed to import CSV");
    } finally {
      setCsvImportLoading(false);
    }
  };

  const handleCreateOrUpdateTestData = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newValKey.trim() || !newValValue.trim()) {
      alert("Key and Value are required");
      return;
    }
    setValSubmitLoading(true);
    try {
      const created = await apiRequest(`/testcases/${projectId}/testdata`, {
        method: "POST",
        body: JSON.stringify({
          key: newValKey.toUpperCase().replace(/\s+/g, "_"),
          value: newValValue,
          description: newValDesc
        })
      });
      setTestDataList(prev => {
        const exists = prev.some(item => item.key === created.key);
        if (exists) {
          return prev.map(item => item.key === created.key ? created : item);
        }
        return [...prev, created];
      });
      setNewValKey("");
      setNewValValue("");
      setNewValDesc("");
    } catch (err: any) {
      alert(err.message || "Failed to update variable");
    } finally {
      setValSubmitLoading(false);
    }
  };

  const handleDeleteTestData = async (dataId: number) => {
    try {
      await apiRequest(`/testcases/${projectId}/testdata/${dataId}`, {
        method: "DELETE"
      });
      setTestDataList(prev => prev.filter(item => item.id !== dataId));
    } catch (err: any) {
      alert(err.message || "Failed to delete variable");
    }
  };

  const handleGeneratePlaywrightScript = async (tc: any) => {
    setSelectedTestCase(tc);
    setScriptLoading(true);
    setGeneratedScript("");
    try {
      const res = await apiRequest(`/testcases/${projectId}/generate-automation/${tc.id}`, {
        method: "POST"
      });
      setGeneratedScript(res.script);
    } catch (err: any) {
      alert(err.message || "Failed to generate script");
    } finally {
      setScriptLoading(false);
    }
  };

  const handleDownloadTemplate = () => {
    const csvContent = "data:text/csv;charset=utf-8,title,description,steps,expected_result,test_data\n"
      + '"User Login","Verify login page works","1. Navigate to login page\\n2. Enter credentials\\n3. Click Login","Dashboard page is displayed","{""username"": ""test"", ""password"": ""secret""}"\n';
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "testforge_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportCSV = async () => {
    try {
      const token = localStorage.getItem("token") || "";
      const response = await fetch(`http://localhost:8000/api/testcases/${projectId}/export`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error("Failed to export CSV");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `testforge_cases_project_${projectId}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.message || "Failed to export CSV");
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col h-screen overflow-hidden">
      {/* Workspace Navbar */}
      <header className="border-b border-gray-900 bg-gray-950/80 backdrop-blur-md px-6 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/")}
            className="p-2 rounded-lg border border-gray-900 hover:bg-gray-900 text-gray-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 uppercase tracking-widest">Project Space</span>
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" />
            </div>
            <h1 className="text-lg font-bold">{project?.name || "Loading Project..."}</h1>
          </div>

          {/* Mode Selector */}
          <div className="flex bg-gray-900/60 p-1 rounded-xl border border-gray-800 ml-8">
            <button
              onClick={() => setWorkspaceMode("unit")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                workspaceMode === "unit"
                  ? "bg-indigo-650 text-white shadow-md shadow-indigo-650/20"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <Code className="h-3.5 w-3.5" />
              <span>Unit & Code Testing</span>
            </button>
            <button
              onClick={() => setWorkspaceMode("qa")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                workspaceMode === "qa"
                  ? "bg-indigo-650 text-white shadow-md shadow-indigo-650/20"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <FileSpreadsheet className="h-3.5 w-3.5" />
              <span>QA Automation & Test Cases</span>
            </button>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex items-center gap-3">
          {workspaceMode === "unit" ? (
            <button
              onClick={handleRunTests}
              disabled={runLoading || files.length === 0}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4.5 py-2.5 text-xs font-bold hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer disabled:opacity-50"
            >
              {runLoading ? (
                <>
                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  <span>Running PyTest...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Execute PyTest Suite</span>
                </>
              )}
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownloadTemplate}
                className="flex items-center gap-1.5 rounded-lg border border-gray-800 bg-gray-900/50 hover:bg-gray-900 px-3.5 py-2 text-xs font-semibold text-gray-300 hover:text-white transition-all cursor-pointer"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download Template</span>
              </button>
              
              <label className="flex items-center gap-1.5 rounded-lg border border-gray-800 bg-gray-900/50 hover:bg-gray-900 px-3.5 py-2 text-xs font-semibold text-gray-300 hover:text-white transition-all cursor-pointer">
                <Upload className="h-3.5 w-3.5 text-indigo-400" />
                <span>{csvImportLoading ? "Importing..." : "Import CSV"}</span>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleImportCSV}
                  disabled={csvImportLoading}
                  className="hidden"
                />
              </label>

              <button
                onClick={handleExportCSV}
                className="flex items-center gap-1.5 rounded-lg border border-gray-800 bg-gray-900/50 hover:bg-gray-900 px-3.5 py-2 text-xs font-semibold text-gray-300 hover:text-white transition-all cursor-pointer"
              >
                <Download className="h-3.5 w-3.5 text-emerald-400" />
                <span>Export CSV</span>
              </button>

              <button
                onClick={() => setShowTcModal(true)}
                className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-bold hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Test Case</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Workspace split panel */}
      <div className="flex flex-1 overflow-hidden">
        {workspaceMode === "unit" ? (
          <>
            {/* Left Column: Code Explorer */}
            <aside className="w-80 border-r border-gray-900 bg-gray-950 flex flex-col overflow-hidden shrink-0">
              <div className="p-4 border-b border-gray-900">
                <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400">Project Files</h2>
                <div className="mt-3 relative">
                  <label className="flex items-center justify-center gap-2 rounded-lg border border-dashed border-gray-800 bg-gray-900/30 px-4 py-4.5 text-xs text-gray-400 hover:text-white hover:border-indigo-500/50 hover:bg-indigo-950/10 transition-all cursor-pointer">
                    <Upload className="h-4 w-4 text-indigo-400" />
                    <span>{uploadLoading ? "Uploading..." : "Upload Python File"}</span>
                    <input
                      type="file"
                      accept=".py"
                      onChange={handleFileUpload}
                      disabled={uploadLoading}
                      className="hidden"
                      multiple
                    />
                  </label>
                </div>
              </div>

              {/* Files List */}
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {files.map((file) => (
                  <button
                    key={file.id}
                    onClick={() => handleSelectFile(file)}
                    className={`w-full flex items-center justify-between gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium transition-all cursor-pointer ${
                      selectedFile?.id === file.id
                        ? "bg-indigo-950/30 text-indigo-300 border border-indigo-500/20"
                        : "text-gray-400 hover:bg-gray-900 hover:text-white border border-transparent"
                    }`}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <FileCode className="h-4 w-4 text-indigo-400 shrink-0" />
                      <span className="truncate">{file.filename}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* AST Tree Panel */}
              {selectedFile && analysis && (
                <div className="h-1/2 border-t border-gray-900 flex flex-col overflow-hidden">
                  <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                      <Layers className="h-3.5 w-3.5 text-cyan-400" />
                      <span>AST Code Elements</span>
                    </h2>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {/* Classes list */}
                    {analysis.classes.length > 0 && (
                      <div>
                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1.5">Classes</h3>
                        <div className="space-y-1">
                          {analysis.classes.map((cls) => (
                            <button
                              key={cls.name}
                              onClick={() => handleSelectElement(cls.name, "class")}
                              className={`w-full text-left px-2 py-1.5 rounded text-xs truncate flex items-center gap-2 cursor-pointer ${
                                selectedElement?.name === cls.name
                                  ? "bg-indigo-950/20 text-indigo-400 font-bold"
                                  : "text-gray-300 hover:bg-gray-900"
                              }`}
                            >
                              <span className="text-cyan-400 text-xs font-black">C</span>
                              <span className="truncate">{cls.name}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Functions list */}
                    {analysis.functions.length > 0 && (
                      <div>
                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1.5">Functions</h3>
                        <div className="space-y-1">
                          {analysis.functions.map((func) => (
                            <button
                              key={func.name}
                              onClick={() => handleSelectElement(func.name, "function")}
                              className={`w-full text-left px-2 py-1.5 rounded text-xs truncate flex items-center gap-2 cursor-pointer ${
                                selectedElement?.name === func.name
                                  ? "bg-indigo-950/20 text-indigo-400 font-bold"
                                  : "text-gray-300 hover:bg-gray-900"
                              }`}
                            >
                              <span className="text-indigo-400 text-xs font-black">F</span>
                              <span className="truncate">{func.name}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {analysis.classes.length === 0 && analysis.functions.length === 0 && (
                      <p className="text-xs text-gray-600 italic">No classes or functions parsed in file.</p>
                    )}
                  </div>
                </div>
              )}
            </aside>

            {/* Center Column: Workspace Code Editor */}
            <section className="flex-1 border-r border-gray-900 bg-gray-950/50 flex flex-col overflow-hidden">
              {selectedFile ? (
                <>
                  {/* Tab Header Toolbar */}
                  <div className="px-6 py-2.5 border-b border-gray-900 flex items-center justify-between shrink-0 bg-gray-950">
                    <div className="flex gap-1.5">
                      <button
                        onClick={() => setActiveTab("source")}
                        className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                          activeTab === "source"
                            ? "bg-gray-900 text-white border border-gray-800"
                            : "text-gray-400 hover:text-white"
                        }`}
                      >
                        <Code className="h-3.5 w-3.5" />
                        <span>Source Code</span>
                      </button>
                      <button
                        onClick={() => setActiveTab("tests")}
                        className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                          activeTab === "tests"
                            ? "bg-gray-900 text-white border border-gray-800"
                            : "text-gray-400 hover:text-white"
                        }`}
                      >
                        <FileText className="h-3.5 w-3.5" />
                        <span>Generated PyTest</span>
                      </button>
                    </div>

                    {activeTab === "tests" && (
                      <button
                        onClick={handleSaveTest}
                        disabled={saveLoading}
                        className="flex items-center gap-2 rounded-lg bg-gray-900 border border-gray-800 hover:border-gray-700 px-3.5 py-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-all cursor-pointer disabled:opacity-50"
                      >
                        <Save className="h-3.5 w-3.5" />
                        <span>{saveLoading ? "Saving..." : "Save Test File"}</span>
                      </button>
                    )}
                  </div>

                  {/* Status Banner */}
                  {testSuccessMessage && (
                    <div className="bg-indigo-950/30 border-b border-indigo-500/20 px-6 py-3 text-xs text-indigo-300 flex items-center gap-2 shrink-0">
                      <Terminal className="h-4 w-4 text-indigo-400 shrink-0" />
                      <span>{testSuccessMessage}</span>
                    </div>
                  )}

                  {/* Code Editor Body */}
                  <div className="flex-1 overflow-hidden p-6 bg-gray-950">
                    {activeTab === "source" ? (
                      <pre className="h-full overflow-y-auto bg-gray-900/40 border border-gray-900 rounded-xl p-4 text-xs font-mono text-gray-300 leading-relaxed tab-size-4 select-text">
                        <code>{fileContent}</code>
                      </pre>
                    ) : (
                      <textarea
                        value={testContent}
                        onChange={(e) => setTestContent(e.target.value)}
                        className="w-full h-full bg-gray-900/40 border border-gray-900 rounded-xl p-4 text-xs font-mono text-gray-300 leading-relaxed outline-none focus:border-indigo-500/30 transition-all resize-none"
                        spellCheck="false"
                      />
                    )}
                  </div>
                </>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-6 bg-gray-950">
                  <FileCode className="h-12 w-12 text-gray-700 mb-4" />
                  <h3 className="text-lg font-bold">No File Selected</h3>
                  <p className="text-gray-400 max-w-xs text-sm mt-2">
                    Upload or select a Python file on the left navigation to open the workspace.
                  </p>
                </div>
              )}
            </section>

            {/* Right Column: AI Suggestions & History */}
            <aside className="w-96 bg-gray-950 flex flex-col overflow-hidden shrink-0">
              {selectedElement ? (
                // AI Copilot Panel
                <div className="flex flex-col h-full overflow-hidden">
                  <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-purple-400 animate-pulse" />
                        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400">Gemini Edge Cases</h2>
                      </div>
                      <button
                        onClick={() => setSelectedElement(null)}
                        className="text-[10px] text-gray-500 hover:text-white cursor-pointer"
                      >
                        Clear Selection
                      </button>
                    </div>
                    <div className="mt-2 flex items-center gap-1.5 text-xs font-semibold text-indigo-400 bg-indigo-950/15 border border-indigo-500/10 rounded px-2 py-1">
                      <span>Target: {selectedElement.name} ({selectedElement.type})</span>
                    </div>
                  </div>

                  {/* Suggestions list */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {aiLoading ? (
                      <div className="flex flex-col items-center justify-center py-16 text-center gap-3 bg-gray-950">
                        <span className="h-7 w-7 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
                        <p className="text-xs text-gray-400 animate-pulse">Gemini is analyzing edge cases...</p>
                      </div>
                    ) : aiError ? (
                      <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-xs text-red-400 flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                        <div>
                          <p className="font-bold">AI Analysis Failed</p>
                          <p className="mt-1 leading-normal">{aiError}</p>
                        </div>
                      </div>
                    ) : aiSuggestions.length === 0 ? (
                      <p className="text-xs text-gray-500 italic text-center py-8">No suggestions returned.</p>
                    ) : (
                      aiSuggestions.map((sug, idx) => (
                        <div key={idx} className="glass-card rounded-xl p-4 space-y-3 border border-gray-900 bg-gray-900/10">
                          <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
                            {sug.title}
                          </h4>
                          <p className="text-[11px] text-gray-400 leading-relaxed font-sans">
                            {sug.explanation}
                          </p>
                          
                          <div className="relative group bg-black/60 rounded-lg p-2.5 border border-gray-950">
                            <pre className="text-[10px] font-mono text-gray-300 overflow-x-auto whitespace-pre select-text pr-8 max-h-32">
                              <code>{sug.test_code}</code>
                            </pre>
                            
                            <div className="absolute top-2 right-2 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button
                                onClick={() => handleCopyCode(sug.test_code, `sug_${idx}`)}
                                className="p-1 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 transition-colors cursor-pointer"
                                title="Copy Code"
                              >
                                {copySuccessMap[`sug_${idx}`] ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                              </button>
                              <button
                                onClick={() => handleAppendTest(sug.test_code)}
                                className="p-1 rounded bg-indigo-650 text-white hover:bg-indigo-500 transition-colors cursor-pointer"
                                title="Add to Test Suite"
                              >
                                <Plus className="h-3 w-3" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ) : (
                // Runs History & Default View
                <div className="flex flex-col h-full overflow-hidden">
                  <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                      <History className="h-4 w-4 text-emerald-400" />
                      <span>Execution History</span>
                    </h2>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-950">
                    {runs.length === 0 ? (
                      <div className="text-center py-16 text-gray-500 space-y-2">
                        <Clock className="h-8 w-8 text-gray-700 mx-auto" />
                        <p className="text-xs italic">No test runs executed yet.</p>
                      </div>
                    ) : (
                      runs.map((run) => (
                        <div
                          key={run.id}
                          onClick={() => router.push(`/projects/${projectId}/runs/${run.id}`)}
                          className="glass-card rounded-xl p-3.5 border border-gray-900 hover:border-gray-800 bg-gray-900/10 transition-all cursor-pointer flex flex-col gap-2 group"
                        >
                          <div className="flex items-center justify-between">
                            <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                              run.status === "passed" ? "bg-emerald-950/60 text-emerald-400 border border-emerald-500/20" : "bg-rose-950/60 text-rose-400 border border-rose-500/20"
                            }`}>
                              {run.status}
                            </span>
                            <span className="text-[10px] text-gray-500">
                              {new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-300 font-semibold group-hover:text-indigo-400 transition-colors">
                              Run #{run.id}
                            </span>
                            <span className="text-gray-400">
                              Coverage: <strong className="text-white">{run.coverage_percentage}%</strong>
                            </span>
                          </div>
                          
                          <div className="text-[10px] text-gray-500 flex justify-between">
                            <span>Passed: {run.passed_count} | Failed: {run.failed_count}</span>
                            <span className="text-indigo-400 group-hover:underline">View Report</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </aside>
          </>
        ) : (
          // QA Automation & Test Cases Dashboard View
          <div className="flex-1 flex overflow-hidden bg-gray-950">
            {/* Left Column: Test Case Manager */}
            <section className="flex-1 border-r border-gray-900 bg-gray-950/20 flex flex-col overflow-hidden">
              <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950 flex items-center justify-between">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                    <FileSpreadsheet className="h-4 w-4 text-indigo-450" />
                    <span>Test Case Repository</span>
                  </h2>
                  <p className="text-[10px] text-gray-500 mt-0.5">Manage business test flows and export to Excel/CSV</p>
                </div>
                <div className="text-[10px] bg-gray-900 border border-gray-800 text-gray-400 px-2 py-0.5 rounded">
                  Total Cases: <strong className="text-white">{testCases.length}</strong>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {testCases.length === 0 ? (
                  <div className="text-center py-24 text-gray-500 space-y-3">
                    <FileSpreadsheet className="h-10 w-10 text-gray-700 mx-auto" />
                    <p className="text-sm font-semibold">No test cases imported yet</p>
                    <p className="text-xs text-gray-650 max-w-xs mx-auto">
                      Click the "Import CSV" button to load test cases from Excel or create one using "Add Test Case".
                    </p>
                  </div>
                ) : (
                  <div className="border border-gray-900 rounded-xl overflow-hidden bg-gray-900/10">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-gray-900 bg-gray-900/40 text-gray-400 font-bold">
                          <th className="p-3">Title & Description</th>
                          <th className="p-3">Steps</th>
                          <th className="p-3">Expected Result</th>
                          <th className="p-3 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {testCases.map((tc) => (
                          <tr 
                            key={tc.id} 
                            onClick={() => handleGeneratePlaywrightScript(tc)}
                            className={`border-b border-gray-900/60 hover:bg-gray-900/30 transition-colors cursor-pointer ${
                              selectedTestCase?.id === tc.id ? "bg-indigo-950/20 border-l-2 border-l-indigo-500" : ""
                            }`}
                          >
                            <td className="p-3 max-w-xs">
                              <div className="font-bold text-white truncate">{tc.title}</div>
                              {tc.description && (
                                <div className="text-[10px] text-gray-500 truncate mt-0.5">{tc.description}</div>
                              )}
                            </td>
                            <td className="p-3 max-w-xs font-mono text-[10px] text-gray-400 whitespace-pre-wrap leading-normal">
                              {tc.steps}
                            </td>
                            <td className="p-3 max-w-xs text-gray-400">
                              {tc.expected_result}
                            </td>
                            <td className="p-3 text-right" onClick={(e) => e.stopPropagation()}>
                              <div className="flex justify-end gap-1.5">
                                <button
                                  onClick={() => handleGeneratePlaywrightScript(tc)}
                                  className="p-1 rounded bg-indigo-650/20 border border-indigo-500/20 hover:bg-indigo-600 hover:text-white text-indigo-400 transition-colors cursor-pointer text-[10px] px-2 font-bold flex items-center gap-1"
                                  title="Generate Script"
                                >
                                  <Sparkles className="h-3 w-3" />
                                  <span>Automate</span>
                                </button>
                                <button
                                  onClick={() => handleDeleteTestCase(tc.id)}
                                  className="p-1.5 rounded bg-gray-900 border border-gray-800 text-gray-500 hover:text-red-400 hover:border-red-500/20 transition-colors cursor-pointer"
                                  title="Delete Case"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </section>

            {/* Middle Column: Test Data & Variables */}
            <aside className="w-80 border-r border-gray-900 bg-gray-950 flex flex-col overflow-hidden shrink-0">
              <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950">
                <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                  <Database className="h-4 w-4 text-emerald-450" />
                  <span>Externalized Test Data</span>
                </h2>
                <p className="text-[10px] text-gray-500 mt-0.5">Parameters injected into Playwright scripts</p>
              </div>

              {/* Test Data Variables List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {testDataList.length === 0 ? (
                  <p className="text-xs text-gray-650 italic text-center py-6">No config variables defined yet.</p>
                ) : (
                  <div className="space-y-2">
                    {testDataList.map((item) => (
                      <div key={item.id} className="bg-gray-900/30 border border-gray-900 rounded-xl p-3 space-y-1 relative group">
                        <button
                          onClick={() => handleDeleteTestData(item.id)}
                          className="absolute top-2 right-2 p-1 rounded bg-black/40 border border-gray-850 text-gray-500 hover:text-red-400 hover:border-red-500/20 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                        <div className="text-[10px] font-bold font-mono text-emerald-400 break-all">{item.key}</div>
                        <div className="text-xs text-gray-300 font-mono break-all">{item.value}</div>
                        {item.description && (
                          <div className="text-[9px] text-gray-600 mt-1 italic leading-normal">{item.description}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Add Test Data Form */}
              <div className="p-4 border-t border-gray-900 bg-gray-950/80 shrink-0">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1">
                  <Plus className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Add Variable</span>
                </h3>
                <form onSubmit={handleCreateOrUpdateTestData} className="space-y-2 text-xs">
                  <input
                    type="text"
                    value={newValKey}
                    onChange={(e) => setNewValKey(e.target.value)}
                    placeholder="e.g. BASE_URL"
                    className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50 uppercase font-mono"
                    required
                  />
                  <input
                    type="text"
                    value={newValValue}
                    onChange={(e) => setNewValValue(e.target.value)}
                    placeholder="Value (e.g. http://127.0.0.1:3000)"
                    className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50 font-mono"
                    required
                  />
                  <input
                    type="text"
                    value={newValDesc}
                    onChange={(e) => setNewValDesc(e.target.value)}
                    placeholder="Description (optional)"
                    className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50"
                  />
                  <button
                    type="submit"
                    disabled={valSubmitLoading}
                    className="w-full rounded-lg bg-indigo-650 hover:bg-indigo-600 px-3 py-2 text-xs font-bold text-white transition-all cursor-pointer disabled:opacity-50"
                  >
                    {valSubmitLoading ? "Saving Variable..." : "Save Parameter"}
                  </button>
                </form>
              </div>
            </aside>

            {/* Right Column: Playwright Script Generator */}
            <aside className="w-96 bg-gray-950 flex flex-col overflow-hidden shrink-0">
              <div className="p-4 border-b border-gray-900 shrink-0 bg-gray-950">
                <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-purple-400 animate-pulse" />
                  <span>QA automation scripts</span>
                </h2>
                <p className="text-[10px] text-gray-500 mt-0.5">Auto-generated Playwright test automation code</p>
              </div>

              {selectedTestCase ? (
                <div className="flex flex-1 flex-col overflow-hidden bg-gray-950">
                  {/* Test case metadata */}
                  <div className="p-4 border-b border-gray-900 bg-gray-900/10 shrink-0 space-y-2">
                    <div className="text-[10px] font-bold text-indigo-400 uppercase">Selected Case:</div>
                    <div className="text-xs font-bold text-white">{selectedTestCase.title}</div>
                    <div className="text-[10px] text-gray-500 leading-normal font-mono whitespace-pre-wrap max-h-24 overflow-y-auto bg-black/40 p-2 border border-gray-900 rounded-lg">
                      <strong>Steps:</strong><br />
                      {selectedTestCase.steps}
                    </div>
                  </div>

                  {/* Generated script container */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {scriptLoading ? (
                      <div className="flex flex-col items-center justify-center py-24 text-center gap-3">
                        <span className="h-7 w-7 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
                        <p className="text-xs text-gray-400 animate-pulse">Gemini is translating test to Playwright...</p>
                      </div>
                    ) : generatedScript ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-gray-500 uppercase">Playwright Python Script</span>
                          <button
                            onClick={() => handleCopyCode(generatedScript, "automation_script")}
                            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-gray-900 border border-gray-800 text-[10px] text-gray-300 hover:text-white hover:border-gray-700 transition-colors cursor-pointer"
                          >
                            {copySuccessMap["automation_script"] ? (
                              <>
                                <Check className="h-3.5 w-3.5 text-emerald-400" />
                                <span>Copied!</span>
                              </>
                            ) : (
                              <>
                                <Copy className="h-3.5 w-3.5" />
                                <span>Copy Code</span>
                              </>
                            )}
                          </button>
                        </div>
                        <div className="relative group bg-black/60 rounded-xl p-3 border border-gray-900">
                          <pre className="text-[10px] font-mono text-gray-300 overflow-x-auto whitespace-pre select-text leading-relaxed">
                            <code>{generatedScript}</code>
                          </pre>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-16 text-gray-500 space-y-2">
                        <Sparkles className="h-8 w-8 text-gray-700 mx-auto" />
                        <p className="text-xs italic">Select a test case and click "Automate" to generate the automation script.</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-6 bg-gray-950">
                  <Code className="h-10 w-10 text-gray-700 mb-3" />
                  <p className="text-xs text-gray-500 italic max-w-xs mx-auto">
                    Select a test case from the repository list to generate and view its corresponding automation scripts.
                  </p>
                </div>
              )}
            </aside>
          </div>
        )}
      </div>

      {/* Modal for creating a Test Case */}
      {showTcModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl relative">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-indigo-450" />
              <span>Create New Test Case</span>
            </h2>
            <form onSubmit={handleCreateTestCase} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-gray-400 font-medium mb-1">Title *</label>
                <input
                  type="text"
                  value={newTcTitle}
                  onChange={(e) => setNewTcTitle(e.target.value)}
                  className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50"
                  placeholder="e.g. User Signup Success"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-400 font-medium mb-1">Description</label>
                <input
                  type="text"
                  value={newTcDesc}
                  onChange={(e) => setNewTcDesc(e.target.value)}
                  className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50"
                  placeholder="e.g. Verify user can register with valid credentials"
                />
              </div>
              <div>
                <label className="block text-gray-400 font-medium mb-1">Steps (one per line) *</label>
                <textarea
                  value={newTcSteps}
                  onChange={(e) => setNewTcSteps(e.target.value)}
                  className="w-full h-24 bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50 resize-none font-mono"
                  placeholder="1. Go to signup page&#10;2. Enter unique email&#10;3. Click submit"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-400 font-medium mb-1">Expected Result *</label>
                <textarea
                  value={newTcExpected}
                  onChange={(e) => setNewTcExpected(e.target.value)}
                  className="w-full h-16 bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50 resize-none"
                  placeholder="User dashboard is displayed with welcome alert"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-400 font-medium mb-1">Test Data (JSON Format, optional)</label>
                <input
                  type="text"
                  value={newTcData}
                  onChange={(e) => setNewTcData(e.target.value)}
                  className="w-full bg-black border border-gray-850 rounded-lg p-2 text-white outline-none focus:border-indigo-500/50 font-mono"
                  placeholder='e.g. {"email": "test@example.com"}'
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTcModal(false)}
                  className="px-4 py-2 rounded-lg border border-gray-800 hover:bg-gray-800 text-gray-400 transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={tcSubmitLoading}
                  className="px-4 py-2 rounded-lg bg-indigo-650 hover:bg-indigo-600 text-white font-bold transition-all cursor-pointer disabled:opacity-50"
                >
                  {tcSubmitLoading ? "Creating..." : "Create Test Case"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
