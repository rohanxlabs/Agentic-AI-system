"use client";

import { useState, useRef, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToasts } from "@/hooks/use-toast-notifier";
import { runSystemStream, StreamEvent } from "@/services/api";
import { Loader2, Brain, Code, TrendingUp, Users } from "lucide-react";

const formSchema = z.object({
  goal: z.string().min(1, "Goal is required"),
  enableTools: z.boolean(),
});

type FormValues = {
  goal: string;
  enableTools: boolean;
};

type Step = {
  id: number;
  agent: string;
  content: string;
  step: number;
};

function isStepEvent(event: StreamEvent): event is { type: "step_result"; agent: string; content: string; step: number } {
  return event.type === "step_result";
}

export default function Workspace() {
  const { register, handleSubmit, watch } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      goal: "",
      enableTools: true,
    },
  });

  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);
  const [isAborted, setIsAborted] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { success, error: toastError } = useToasts();
  const messagesRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (messagesRef.current) {
      messagesRef.current.scrollTo({
        top: messagesRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [steps]);

  const onRun = async () => {
    const values = watch();
    await handleSubmitForm(values);
  };

  const handleSubmitForm = async (data: FormValues) => {
    setIsRunning(true);
    setSteps([]);
    setIsAborted(false);

    abortControllerRef.current = new AbortController();

    try {
      const stream = runSystemStream(
        { goal: data.goal, enable_tools: data.enableTools },
        { signal: abortControllerRef.current.signal }
      );

      let stepCount = 0;
      for await (const event of stream) {
        if (isAborted) break;

        stepCount++;
        if (isStepEvent(event)) {
          setSteps((prev) => [
            ...prev,
            {
              id: Date.now() + stepCount,
              agent: event.agent || "Executor",
              content: event.content,
              step: stepCount,
            },
          ]);
        }
      }

      if (!isAborted) {
        success("Task completed", "The agent has finished processing your request");
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        toastError("Execution failed", (err as Error).message);
      }
    } finally {
      setIsRunning(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    setIsAborted(true);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsRunning(false);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
        <div className="flex-1 lg:w-1/2">
          <h1 className="text-2xl font-bold text-foreground mb-4">AI Workspace</h1>
          <p className="text-muted-foreground">
            Enter your goal below and watch the AI agents work together to solve it.
          </p>
        </div>

        <div className="flex-1 lg:w-1/2 lg:mt-0 lg:flex lg:items-end lg:justify-end space-x-4">
          {!isRunning ? (
            <Button
              variant="default"
              onClick={onRun}
              className="w-full lg:w-auto"
            >
              Run Agent
            </Button>
          ) : (
            <Button
              variant="destructive"
              onClick={handleStop}
              className="w-full lg:w-auto"
            >
              Stop
            </Button>
          )}
        </div>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); onRun(); }} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground block mb-1">
            Goal
          </label>
          <textarea
            {...register("goal")}
            placeholder="Enter your goal (e.g., 'Write a Python function to calculate factorial')"
            className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none min-h-[80px]"
          />
        </div>

        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="enableTools"
            {...register("enableTools")}
            className="h-4 w-4 text-primary rounded border-gray-300 focus:ring-primary"
          />
          <label htmlFor="enableTools" className="text-sm font-medium text-muted-foreground">
            Enable tool usage
          </label>
        </div>
      </form>

      <div className="border rounded-lg border-border bg-card/50">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">
            Execution Steps
          </h2>
          <div className="text-sm text-muted-foreground">
            {steps.length} steps completed
          </div>
        </div>
        <ScrollArea className="h-96">
          <div className="p-4 space-y-4" ref={messagesRef}>
            {steps.map((step) => (
              <div key={step.id} className="flex w-full gap-4">
                <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md bg-primary/20 text-primary">
                  {step.agent === "Planner" && (
                    <Brain className="h-4 w-4" />
                  )}
                  {step.agent === "Executor" && (
                    <Code className="h-4 w-4" />
                  )}
                  {step.agent === "Critic" && (
                    <TrendingUp className="h-4 w-4" />
                  )}
                  {step.agent === "Manager" && (
                    <Users className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1 bg-card p-3 rounded-lg border border-border">
                  <p className="font-medium text-foreground">{step.agent}</p>
                  <p className="text-sm text-muted-foreground">Step {step.step}</p>
                  <div className="mt-2 whitespace-pre-wrap break-words">
                    {step.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
        {isRunning && !isAborted && (
          <div className="flex items-center justify-center px-4 py-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 mr-2" /> Processing...
          </div>
        )}
        {!isRunning && steps.length === 0 && (
          <div className="flex items-center justify-center px-4 py-8 text-muted-foreground">
            No steps yet. Run a task to see the agent&apos;s thought process.
          </div>
        )}
      </div>
    </div>
  );
}
