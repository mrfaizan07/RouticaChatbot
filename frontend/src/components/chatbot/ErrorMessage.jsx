import React from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "../common/Button";

export function ErrorMessage({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className="flex items-start gap-2.5 my-3 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 animate-fade-in">
      <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="font-medium">{message}</p>
        {onRetry && (
          <div className="mt-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={onRetry}
              icon={RotateCcw}
              className="text-xs py-1 px-2.5 border-red-200 hover:bg-red-100/50 text-red-700"
            >
              Retry
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

