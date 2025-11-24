"use client";

import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Home() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);
  const [navigatingTo, setNavigatingTo] = useState<string>("");

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleNavigation = (path: string) => (e: React.MouseEvent<HTMLAnchorElement>) => {
    setIsNavigating(true);
    setNavigatingTo(path);
  };

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-md rounded-lg bg-white p-8 shadow-md">
        <div className="text-center">
          <h1 className="mb-8 text-3xl font-bold text-gray-900">DRF Auth App</h1>

          {user ? (
            <div className="space-y-4">
              <div className="text-lg text-gray-700">Welcome!</div>
              <div className="text-sm text-gray-500">Email: {user.email}</div>
              <div className="text-sm text-gray-500">Email Verified: {user.is_email_verified ? "✅" : "❌"}</div>
              <button
                onClick={handleLogout}
                className="flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:outline-none">
                Logout
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="mb-6 text-lg text-gray-700">Please sign in or create an account</div>
              <div className="space-y-3">
                <Link
                  href="/auth/login"
                  onClick={handleNavigation("/auth/login")}
                  className={`flex w-full justify-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white shadow-sm focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none ${
                    isNavigating && navigatingTo === "/auth/login" ? "cursor-not-allowed bg-indigo-400" : "bg-indigo-600 hover:bg-indigo-700"
                  }`}>
                  {isNavigating && navigatingTo === "/auth/login" ? (
                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      <span>Loading...</span>
                    </div>
                  ) : (
                    "Sign In"
                  )}
                </Link>
                <Link
                  href="/auth/register"
                  onClick={handleNavigation("/auth/register")}
                  className={`flex w-full justify-center rounded-md border px-4 py-2 text-sm font-medium shadow-sm focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none ${
                    isNavigating && navigatingTo === "/auth/register"
                      ? "cursor-not-allowed border-gray-300 bg-gray-100 text-gray-400"
                      : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                  }`}>
                  {isNavigating && navigatingTo === "/auth/register" ? (
                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent"></div>
                      <span>Loading...</span>
                    </div>
                  ) : (
                    "Create Account"
                  )}
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
