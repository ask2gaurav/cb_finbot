import { useEffect } from "react";
import { Outlet, useNavigate, Link, useLocation } from "react-router";
import { useAuthStore } from "../lib/auth";

export default function AdminLayout() {
  const { role, token } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!token) navigate("/login");
    else if (role !== "admin") navigate("/chat");
  }, [role, token, navigate]);

  if (role !== "admin") return null;

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold">Admin Panel</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
           <Link to="/admin/users" className={`block px-4 py-2 rounded ${location.pathname.includes('users') ? 'bg-blue-600' : 'hover:bg-gray-800'}`}>Users</Link>
           <Link to="/admin/documents" className={`block px-4 py-2 rounded ${location.pathname.includes('documents') ? 'bg-blue-600' : 'hover:bg-gray-800'}`}>Documents</Link>
           <Link to="/chat" className="block px-4 py-2 rounded hover:bg-gray-800 border border-gray-700 mt-4">Back to Chat</Link>
        </nav>
      </div>
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}
