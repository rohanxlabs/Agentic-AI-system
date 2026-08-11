"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to workspace immediately
    router.push("/workspace");
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Agentic AI System</h1>
        <p className="text-muted-foreground">Loading workspace...</p>
      </div>
    </div>
  );
}
