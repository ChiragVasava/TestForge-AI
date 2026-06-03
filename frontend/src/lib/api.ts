const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest(path: string, options: RequestInit = {}): Promise<any> {
  const headers: Record<string, string> = {
    ...getAuthHeaders(),
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers as Record<string, string>),
  };
  
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      if (!window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
        window.location.href = "/login";
      }
    }
  }
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(errorData.detail || "An error occurred");
  }
  
  if (response.status === 204) {
    return null;
  }
  
  return response.json();
}
