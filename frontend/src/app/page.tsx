"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { 
  Plus, 
  Folder, 
  Trash2, 
  ExternalLink, 
  LogOut, 
  User, 
  Terminal,
  Activity,
  Layers,
  CheckCircle,
  HelpCircle,
  FileCode,
  ShieldAlert
} from "lucide-react";

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

interface UserProfile {
  email: string;
}

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [error, setError] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const loadData = async () => {
      try {
        const userProfile = await apiRequest("/auth/me");
        setUser(userProfile);
        
        const projectList = await apiRequest("/projects/");
        setProjects(projectList);
      } catch (err: any) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    setError("");
    setSubmitLoading(true);

    try {
      const created = await apiRequest("/projects/", {
        method: "POST",
        body: JSON.stringify({
          name: newProjectName,
          description: newProjectDesc,
        }),
      });

      setProjects((prev) => [...prev, created]);
      setModalOpen(false);
      setNewProjectName("");
      setNewProjectDesc("");
    } catch (err: any) {
      setError(err.message || "Failed to create project.");
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDeleteProject = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this project? This will remove all files, tests, and runs permanently.")) {
      return;
    }

    try {
      await apiRequest(`/projects/${id}`, {
        method: "DELETE",
      });
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete project.");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="flex flex-col items-center gap-4">
          <span className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
          <p className="text-gray-400 text-sm animate-pulse">Loading TestForge workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-gray-900 bg-gray-950/80 backdrop-blur-md sticky top-0 z-10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-500">
            <Terminal className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">
            TestForge<span className="text-glow font-black"> AI</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-full border border-gray-900 bg-gray-900/40 px-3.5 py-1.5 text-xs text-gray-300">
            <User className="h-3.5 w-3.5 text-indigo-400" />
            <span>{user?.email}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg border border-gray-900 px-3 py-1.5 text-xs font-semibold text-gray-400 hover:bg-gray-900 hover:text-white transition-all"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 space-y-10">
        
        {/* Dashboard Title & Trigger */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Project Dashboard</h1>
            <p className="text-gray-400 text-sm mt-1">Manage, analyze, and automate tests for your software repositories.</p>
          </div>
          <button
            onClick={() => setModalOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer self-start sm:self-auto"
          >
            <Plus className="h-4 w-4" />
            <span>Create New Project</span>
          </button>
        </div>

        {/* Global Summary Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="glass-card rounded-xl p-5 flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
              <Folder className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Projects</p>
              <h3 className="text-2xl font-bold mt-0.5">{projects.length}</h3>
            </div>
          </div>

          <div className="glass-card rounded-xl p-5 flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20">
              <FileCode className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Target Code base</p>
              <h3 className="text-2xl font-bold mt-0.5">Python AST</h3>
            </div>
          </div>

          <div className="glass-card rounded-xl p-5 flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Engine Stack</p>
              <h3 className="text-2xl font-bold mt-0.5 text-emerald-400">PyTest</h3>
            </div>
          </div>

          <div className="glass-card rounded-xl p-5 flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
              <Activity className="h-5 w-5 text-purple-400" />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">AI Co-pilot</p>
              <h3 className="text-2xl font-bold mt-0.5 text-purple-400">Gemini 1.5</h3>
            </div>
          </div>
        </div>

        {/* Project Grid */}
        {projects.length === 0 ? (
          <div className="glass-card rounded-2xl p-16 text-center border-dashed border-2 border-gray-800">
            <Folder className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-bold">No Projects Found</h3>
            <p className="text-gray-400 max-w-sm mx-auto text-sm mt-2">
              Welcome to TestForge AI! Get started by creating your first project and uploading python modules.
            </p>
            <button
              onClick={() => setModalOpen(true)}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-600 px-5 py-2.5 text-sm font-semibold hover:from-indigo-500 hover:to-cyan-500 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer"
            >
              <Plus className="h-4 w-4" />
              <span>Create Project</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => router.push(`/projects/${project.id}`)}
                className="glass-card glass-card-hover rounded-xl p-6 flex flex-col justify-between h-56 cursor-pointer relative overflow-hidden group"
              >
                {/* Visual top border indicator */}
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-indigo-500 to-cyan-500 opacity-20 group-hover:opacity-100 transition-opacity" />
                
                <div>
                  <div className="flex items-start justify-between">
                    <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                      {project.name}
                    </h3>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 text-indigo-400 transition-opacity">
                      <span className="text-xs">Open</span>
                      <ExternalLink className="h-3 w-3" />
                    </div>
                  </div>
                  <p className="text-gray-400 text-sm mt-2 line-clamp-3">
                    {project.description || "No description provided."}
                  </p>
                </div>

                <div className="border-t border-gray-900/80 pt-4 mt-4 flex items-center justify-between text-xs text-gray-500">
                  <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                  <button
                    onClick={(e) => handleDeleteProject(project.id, e)}
                    className="p-1.5 rounded-md hover:bg-red-500/10 hover:text-red-400 transition-colors text-gray-500"
                    title="Delete project"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <div className="glass-card w-full max-w-md rounded-2xl p-6 shadow-2xl relative border border-gray-800">
            <h3 className="text-xl font-bold mb-4">Create New Project</h3>
            
            <form onSubmit={handleCreateProject} className="space-y-4">
              {error && (
                <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400">
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Auth Service"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="block w-full mt-2 rounded-lg border border-gray-800 bg-gray-900/50 py-2 px-3 text-sm text-white placeholder-gray-500 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400">
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Describe the modules inside..."
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  className="block w-full mt-2 rounded-lg border border-gray-800 bg-gray-900/50 py-2 px-3 text-sm text-white placeholder-gray-500 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all resize-none"
                />
              </div>

              <div className="flex gap-3 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="rounded-lg border border-gray-800 px-4 py-2 text-sm font-semibold text-gray-400 hover:bg-gray-900 hover:text-white transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitLoading}
                  className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer disabled:opacity-50"
                >
                  {submitLoading ? (
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  ) : (
                    <span>Create</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
