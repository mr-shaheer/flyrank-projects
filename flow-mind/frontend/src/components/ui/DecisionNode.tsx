"use client";

import {
  Handle,
  Position,
  type NodeProps,
} from "@xyflow/react";

export type DecisionNodeData = {
  prompt: string;
  onPromptChange?: (
    nodeId: string,
    prompt: string
  ) => void;
  executionDecision?: "YES" | "NO" | null;
};

export default function DecisionNode({
  id,
  data,
}: NodeProps) {
  const nodeData = data as DecisionNodeData;

  const decision =
    nodeData.executionDecision;

  const isYes = decision === "YES";
  const isNo = decision === "NO";

  return (
    <div
      style={{
        position: "relative",
        width: 280,
        padding: 16,
        border: isYes
          ? "2px solid #22c55e"
          : isNo
          ? "2px solid #ef4444"
          : "1px solid #222",
        borderRadius: 12,
        background: isYes
          ? "#f0fdf4"
          : isNo
          ? "#fef2f2"
          : "#ffffff",
        color: "#111111",
        boxShadow:
          "0 4px 12px rgba(0, 0, 0, 0.08)",
        transition:
          "all 0.2s ease",
      }}
    >
      {/* INPUT */}

      <Handle
        type="target"
        position={Position.Left}
        style={{
          width: 10,
          height: 10,
          background: "#111111",
        }}
      />

      {/* HEADER */}

      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          marginBottom: 4,
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.05em",
          }}
        >
          AI DECISION
        </div>

        {decision && (
          <div
            style={{
              padding: "3px 8px",
              borderRadius: 999,
              fontSize: 10,
              fontWeight: 800,
              color: "#ffffff",
              background: isYes
                ? "#22c55e"
                : "#ef4444",
            }}
          >
            {decision}
          </div>
        )}
      </div>

      <div
        style={{
          fontSize: 11,
          color: "#777777",
          marginBottom: 12,
        }}
      >
        Node {id}
      </div>

      {/* PROMPT */}

      <textarea
        value={nodeData.prompt}
        onChange={(event) => {
          nodeData.onPromptChange?.(
            id,
            event.target.value
          );
        }}
        placeholder="Enter decision question..."
        style={{
          width: "100%",
          minHeight: 80,
          padding: 10,
          border: "1px solid #dddddd",
          borderRadius: 8,
          resize: "vertical",
          fontSize: 13,
          outline: "none",
          boxSizing: "border-box",
          background: "#ffffff",
          color: "#111111",
        }}
      />

      {/* YES HANDLE */}

      <Handle
        type="source"
        position={Position.Right}
        id="yes"
        style={{
          top: "38%",
          width: 11,
          height: 11,
          background: "#22c55e",
        }}
      />

      <span
        style={{
          position: "absolute",
          right: -38,
          top: "33%",
          fontSize: 11,
          fontWeight: 700,
          color: "#16a34a",
        }}
      >
        YES
      </span>

      {/* NO HANDLE */}

      <Handle
        type="source"
        position={Position.Right}
        id="no"
        style={{
          top: "72%",
          width: 11,
          height: 11,
          background: "#ef4444",
        }}
      />

      <span
        style={{
          position: "absolute",
          right: -30,
          top: "67%",
          fontSize: 11,
          fontWeight: 700,
          color: "#dc2626",
        }}
      >
        NO
      </span>
    </div>
  );
}