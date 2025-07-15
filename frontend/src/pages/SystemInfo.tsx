// src/pages/SystemInfo.tsx
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Server, User } from "lucide-react";

interface SystemInfo {
  user: string;
  timestamp: string;
  hostname: string;
}

export default function SystemInfoPage() {
  const [data, setData] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/modules/system-info")
      .then(res => setData(res.data))
      .catch(() => setError("Failed to fetch system info"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-semibold">System Info</h1>
      {loading ? (
        <div className="flex items-center space-x-2 text-gray-500">
          <Loader2 className="animate-spin" />
          <span>Loading...</span>
        </div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : data ? (
        <Card className="max-w-md">
          <CardContent className="p-4 space-y-4">
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5" />
              <span className="font-medium">User:</span>
              <span>{data.user}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Server className="w-5 h-5" />
              <span className="font-medium">Hostname:</span>
              <span>{data.hostname}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-medium">Timestamp:</span>
              <span>{new Date(data.timestamp).toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
