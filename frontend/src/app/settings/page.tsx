"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useToasts } from "@/hooks/use-toast-notifier";
import {
  Server,
  Palette,
  Brush,
  Code,
  Database,
  Clock,
  Settings as SettingsIcon,
  List,
  Zap,
  Info,
  Brain,
} from "lucide-react";

type SettingsForm = {
  theme?: "light" | "dark" | "system";
  language?: string;
  timeout?: number;
  autoSave?: boolean;
  enableLogging?: boolean;
  maxTokens?: number;
  temperature?: number;
  apiUrl?: string;
};

const settingsSchema = z.object({
  theme: z.enum(["light", "dark", "system"]).default("system"),
  language: z.string().default("en"),
  timeout: z.number().min(1000).max(300000).default(30000),
  autoSave: z.boolean().default(true),
  enableLogging: z.boolean().default(false),
  maxTokens: z.number().min(100).max(8000).default(2048),
  temperature: z.number().min(0).max(2).default(0.7),
  apiUrl: z.string().url().default("http://localhost:8000"),
});

export default function Settings() {
  const { register, handleSubmit, reset, watch } = useForm<SettingsForm>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
        theme: "system",
        language: "en",
        timeout: 30000,
        autoSave: true,
        enableLogging: false,
        maxTokens: 2048,
        temperature: 0.7,
        apiUrl: "http://localhost:8000",
      },
  });

  const [isSaving, setIsSaving] = useState(false);
  const { success, error: toastError } = useToasts();

  const onSubmit = async (data: SettingsForm) => {
    setIsSaving(true);
    try {
      // In a real app, we would save to backend or localStorage
      // For now, we'll simulate an API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      success("Settings saved", "Your preferences have been updated");
      
      // If API URL changed, we might need to update the API client
      // This is just a demo, so we'll just show a message
      if (data.apiUrl !== watch("apiUrl")) {
        // In a real app, we would update the API client base URL
        // For now, we'll just note that a restart might be needed
        toastError("Note", "API URL change may require restart");
      }
    } catch (err) {
      toastError("Failed to save settings", (err as Error).message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <div className="flex space-x-4">
          <Button
            variant="outline"
            onClick={() => {
              // Reset to defaults
              reset({
                theme: "system",
                language: "en",
                timeout: 30000,
                autoSave: true,
                maxTokens: 2048,
                temperature: 0.7,
                apiUrl: "http://localhost:8000",
              });
            }}
          >
            Reset to Defaults
          </Button>
          <Button
            variant="default"
            onClick={handleSubmit(onSubmit)}
            disabled={isSaving}
            className="flex items-center gap-2"
          >
            {isSaving ? (
              <>
                <span className="mr-2">Saving...</span>
              </>
            ) : (
              "Save Settings"
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-8">
        {/* Appearance Settings */}
        <Card className="border border-border">
          <CardHeader>
            <h2 className="text-lg font-semibold text-foreground">
              <Palette className="mr-2 h-4 w-4" /> Appearance
            </h2>
          </CardHeader>
          <CardContent className="pt-0 space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  Theme
                </label>
                <Select
                  defaultValue="system"
                   onValueChange={(value: string) => {
                    // In a real app, we would update the theme immediately
                    // For now, we'll just update the form value
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="system">System</SelectItem>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  Language
                </label>
                <Input
                  {...register("language")}
                  placeholder="en"
                  className="w-full"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card className="border border-border">
          <CardHeader>
            <h2 className="text-lg font-semibold text-foreground">
              <Code className="mr-2 h-4 w-4" /> API Configuration
            </h2>
          </CardHeader>
          <CardContent className="pt-0 space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  API URL
                </label>
                <Input
                  {...register("apiUrl")}
                  placeholder="http://localhost:8000"
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  Request Timeout (ms)
                </label>
                <Input
                  type="number"
                  {...register("timeout")}
                  placeholder="30000"
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Maximum time to wait for API responses
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Model Settings */}
        <Card className="border border-border">
          <CardHeader>
            <h2 className="text-lg font-semibold text-foreground">
              <Brain className="mr-2 h-4 w-4" /> Model Parameters
            </h2>
          </CardHeader>
          <CardContent className="pt-0 space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  Max Tokens
                </label>
                <Input
                  type="number"
                  {...register("maxTokens")}
                  placeholder="2048"
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Maximum number of tokens to generate
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground block">
                  Temperature
                </label>
                <Input
                  type="number"
                  step="0.1"
                  {...register("temperature")}
                  placeholder="0.7"
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Controls randomness: 0 = deterministic, 2 = more random
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Advanced Settings */}
        <Card className="border border-border">
          <CardHeader>
            <h2 className="text-lg font-semibold text-foreground">
              <SettingsIcon className="mr-2 h-4 w-4" /> Advanced
            </h2>
          </CardHeader>
          <CardContent className="pt-0 space-y-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Switch
                  {...register("autoSave")}
                  defaultChecked={true}
                  className="h-4 w-4"
                />
                <span className="text-sm font-medium text-foreground">
                  Auto-save conversations
                </span>
              </div>

              <div className="flex items-center space-x-3">
                <Switch
                  {...register("enableLogging")}
                  defaultChecked={false}
                  className="h-4 w-4"
                />
                <span className="text-sm font-medium text-foreground">
                  Enable debug logging
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}