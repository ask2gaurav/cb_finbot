import { useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuthStore } from "../lib/auth";

export default function Index() {
  const token = useAuthStore((state) => state.token);
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      navigate("/chat", { replace: true });
    } else {
      navigate("/login", { replace: true });
    }
  }, [token, navigate]);

  return <div className="p-8 text-center text-gray-500">Redirecting...</div>;
}
