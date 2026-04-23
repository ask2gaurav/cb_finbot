import { useEffect, useState } from "react";
import { fetchApi } from "../lib/api";

export default function AdminUsers() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadUsers = async () => {
    try {
      const data = await fetchApi("/admin/users");
      setUsers(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadUsers(); }, []);

  const toggleActive = async (id: string, current: boolean) => {
    await fetchApi(`/admin/users/${id}?active=${!current}`, { method: "PATCH" });
    loadUsers();
  };

  const deleteUser = async (id: string) => {
    if(confirm("Are you sure?")) {
        await fetchApi(`/admin/users/${id}`, { method: "DELETE" });
        loadUsers();
    }
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">User Management</h2>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
           <thead className="bg-gray-50">
             <tr>
               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
             </tr>
           </thead>
           <tbody className="bg-white divide-y divide-gray-200">
             {users.map((u: any) => (
               <tr key={u.id}>
                 <td className="px-6 py-4 whitespace-nowrap text-sm">{u.email}</td>
                 <td className="px-6 py-4 whitespace-nowrap text-sm">{u.role}</td>
                 <td className="px-6 py-4 whitespace-nowrap text-sm">
                   <button onClick={() => toggleActive(u.id, u.is_active)} className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                     {u.is_active ? 'Active' : 'Inactive'}
                   </button>
                 </td>
                 <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                   <button onClick={() => deleteUser(u.id)} className="text-red-600 hover:text-red-900">Delete</button>
                 </td>
               </tr>
             ))}
           </tbody>
        </table>
      </div>
    </div>
  );
}
