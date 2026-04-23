import { create } from "zustand";

interface AuthState {
  token: string | null;
  role: string | null;
  setAuth: (token: string, role: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("auth_token") : null,
  role: typeof window !== "undefined" ? localStorage.getItem("auth_role") : null,
  setAuth: (token, role) => {
    localStorage.setItem("auth_token", token);
    localStorage.setItem("auth_role", role);
    set({ token, role });
  },
  logout: () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_role");
    set({ token: null, role: null });
  },
}));
