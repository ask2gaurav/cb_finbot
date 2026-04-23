import { useEffect, useState } from "react";
import { fetchApi } from "../lib/api";

const ROLES = ["general", "finance", "engineering", "marketing", "employee", "c_level"];

export default function AdminDocuments() {
  const [docs, setDocs] = useState<any[]>([]);
  const [stats, setStats] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [selectedRole, setSelectedRole] = useState("finance");

  const loadData = async () => {
    try {
      const d = await fetchApi("/documents");
      setDocs(d);
      const s = await fetchApi("/admin/collections");
      setStats(s);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("role", selectedRole);

    try {
      await fetchApi("/documents/upload", {
        method: "POST",
        body: formData
      });
      alert("Upload started in background. Refresh in a few moments.");
      setFile(null);
      loadData();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  const deleteDoc = async (id: string) => {
    if (confirm("Delete this document from Qdrant and Mongo?")) {
      try {
        await fetchApi(`/documents/${id}`, { method: "DELETE" });
        loadData();
      } catch (e) { console.error(e); }
    }
  };

  return (
    <div className="p-8 space-y-8">
      <h2 className="text-2xl font-bold">Document Management</h2>

      {/* Upload Form */}
      <div className="bg-white p-6 shadow rounded-lg max-w-xl">
        <h3 className="text-lg font-medium mb-4">Upload New Document</h3>
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">File</label>
            <input type="file" required onChange={e => setFile(e.target.files?.[0] || null)} className="mt-1 block w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Target Role Collection</label>
            <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm border p-2">
              {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <button type="submit" disabled={uploading} className="bg-blue-600 text-white px-4 py-2 rounded">
            {uploading ? "Uploading..." : "Upload Document"}
          </button>
        </form>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-4">
        {stats.map((s: any) => (
          <div key={s.role} className="bg-white p-4 shadow rounded-lg">
            <h4 className="font-bold text-sm text-gray-500 uppercase">{s.role}</h4>
            <p className="text-2xl mt-2">{s.points_count} <span className="text-sm text-gray-500">chunks</span></p>
          </div>
        ))}
      </div>

      {/* Docs List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">Filename</th>
              <th className="px-6 py-3 text-left">Role</th>
              <th className="px-6 py-3 text-left">Status</th>
              <th className="px-6 py-3 text-left">Error</th>
              <th className="px-6 py-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {docs.map((d: any) => (
              <tr key={d._id}>
                <td className="px-6 py-4">{d.filename}</td>
                <td className="px-6 py-4"><span className="px-2 bg-blue-100 text-blue-800 rounded-full text-xs">{d.role}</span></td>
                <td className="px-6 py-4">{d.status}</td>
                <td className="px-6 py-4 text-red-500 text-xs">{d.error}</td>
                <td className="px-6 py-4"><button onClick={() => deleteDoc(d._id)} className="text-red-600">Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
