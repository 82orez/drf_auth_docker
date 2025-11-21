"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const AdminRedirect = () => {
  const router = useRouter();

  useEffect(() => {
    // Django admin 페이지로 리다이렉트
    window.location.href = "http://localhost:8000/admin/";
  }, []);

  return (
    <div className="flex h-screen items-center justify-center">
      <p>Django Admin 페이지로 이동 중...</p>
    </div>
  );
};

export default AdminRedirect;
