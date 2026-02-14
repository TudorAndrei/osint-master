import type { UIMessage } from "ai";
import { Bot, CircleAlert, Sparkles } from "lucide-react";
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
} from "@/components/ai-elements/prompt-input";
import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion";

type ChatStatus = "submitted" | "streaming" | "ready" | "error";

interface InvestigationChatbotProps {
  investigationId?: string;
  messages: UIMessage[];
  status: ChatStatus;
  error: Error | null | undefined;
  input: string;
  suggestions: string[];
  onInputChange: (value: string) => void;
  onSendMessage: (text: string) => Promise<void>;
  onSendSuggestion: (text: string) => Promise<void>;
  onStop: () => void;
}

export default function InvestigationChatbot({
  investigationId,
  messages,
  status,
  error,
  input,
  suggestions,
  onInputChange,
  onSendMessage,
  onSendSuggestion,
  onStop,
}: InvestigationChatbotProps) {
  const canSend = Boolean(investigationId) && status === "ready";

  return (
    <div className="rounded-xl border bg-card/90 p-4 shadow-sm">
      <div className="mb-3 rounded-lg border bg-gradient-to-r from-slate-100 via-background to-emerald-100 p-3 dark:from-slate-900 dark:to-emerald-950">
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-primary/10 p-1.5 text-primary">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">Investigation Copilot</h3>
            <p className="text-xs text-muted-foreground">Read-only analysis assistant</p>
          </div>
        </div>
      </div>

      <div className="relative h-[500px] rounded-lg border bg-background/60">
        <Conversation>
          <ConversationContent className="gap-4 p-3">
            {messages.length === 0 ? (
              <ConversationEmptyState
                className="py-14"
                icon={<Sparkles className="h-8 w-8" />}
                title="Start your analysis"
                description="Ask for summaries, relationship insights, suspicious clusters, and duplicate hints."
              />
            ) : (
              messages.map((message, messageIndex) => (
                <Message from={message.role} key={message.id}>
                  <MessageContent>
                    {message.parts.map((part, partIndex) => {
                      if (part.type !== "text") {
                        return null;
                      }
                      const isLatestAssistantMessage =
                        message.role === "assistant" && messageIndex === messages.length - 1;
                      return (
                        <MessageResponse
                          key={`${message.id}-${partIndex}`}
                          isAnimating={status === "streaming" && isLatestAssistantMessage}
                        >
                          {part.text}
                        </MessageResponse>
                      );
                    })}
                  </MessageContent>
                </Message>
              ))
            )}
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>
      </div>

      <div className="mt-3">
        <Suggestions className="pb-1">
          {suggestions.map((suggestion) => (
            <Suggestion
              key={suggestion}
              disabled={!canSend}
              onClick={(text) => {
                void onSendSuggestion(text);
              }}
              suggestion={suggestion}
            />
          ))}
        </Suggestions>
      </div>

      <PromptInput
        className="mt-3"
        onSubmit={async ({ text }) => {
          await onSendMessage(text);
        }}
      >
        <PromptInputBody>
          <PromptInputTextarea
            disabled={!canSend}
            onChange={(event) => onInputChange(event.target.value)}
            placeholder="Ask about this investigation..."
            value={input}
          />
        </PromptInputBody>
        <PromptInputFooter>
          <PromptInputTools>
            <p className="px-2 text-xs text-muted-foreground">
              {investigationId ? "Scoped to current investigation" : "Select an investigation"}
            </p>
          </PromptInputTools>
          <PromptInputSubmit
            disabled={!input.trim() || !canSend}
            onStop={onStop}
            status={status}
          />
        </PromptInputFooter>
      </PromptInput>

      {error ? (
        <div className="mt-2 flex items-center gap-1 text-xs text-destructive">
          <CircleAlert className="h-3.5 w-3.5" />
          Something went wrong. Please retry.
        </div>
      ) : null}
    </div>
  );
}
