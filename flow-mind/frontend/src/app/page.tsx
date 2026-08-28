"use client";

import { useCallback, useMemo, useState } from "react";

import {
  ReactFlow,
  Background,
  Controls,
  addEdge,
  useEdgesState,
  useNodesState,
  type Node,
  type Edge,
  type Connection,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import DecisionNode from "@/components/ui/DecisionNode";

// ============================================================
// TYPES
// ============================================================

type ExecutionStep = {
  node_id: string;
  prompt?: string;
  decision: "YES" | "NO";
};

// ============================================================
// INITIAL GRAPH
// ============================================================

const initialNodes: Node[] = [
  {
    id: "1",
    type: "decision",
    position: {
      x: 250,
      y: 200,
    },
    data: {
      prompt: "Is this a support request?",
    },
  },
];

const initialEdges: Edge[] = [];

// ============================================================
// MAIN PAGE
// ============================================================

export default function Home() {
  const [nodes, setNodes, onNodesChange] =
    useNodesState(initialNodes);

  const [edges, setEdges, onEdgesChange] =
    useEdgesState(initialEdges);

  const [nodeCounter, setNodeCounter] =
    useState(2);

  const [userInput, setUserInput] =
    useState("");

  const [execution, setExecution] =
    useState<ExecutionStep[]>([]);

  const [isRunning, setIsRunning] =
    useState(false);

  const [error, setError] =
    useState("");

  // ==========================================================
  // NODE TYPES
  // ==========================================================

  const nodeTypes = useMemo(
    () => ({
      decision: DecisionNode,
    }),
    []
  );

  // ==========================================================
  // UPDATE NODE PROMPT
  // ==========================================================

  const updateNodePrompt = useCallback(
    (nodeId: string, prompt: string) => {
      setNodes((currentNodes) =>
        currentNodes.map((node) => {
          if (node.id !== nodeId) {
            return node;
          }

          return {
            ...node,
            data: {
              ...node.data,
              prompt,
            },
          };
        })
      );
    },
    [setNodes]
  );

  // ==========================================================
  // ADD CALLBACKS + EXECUTION STATE TO NODES
  // ==========================================================

  const nodesWithCallbacks = useMemo(() => {
    return nodes.map((node) => {
      const executedStep = execution.find(
        (step) => step.node_id === node.id
      );

      return {
        ...node,
        data: {
          ...node.data,
          onPromptChange: updateNodePrompt,
          executionDecision:
            executedStep?.decision ?? null,
        },
      };
    });
  }, [nodes, execution, updateNodePrompt]);

  // ==========================================================
  // CONNECT NODES
  // ==========================================================

  const onConnect = useCallback(
    (connection: Connection) => {
      if (
        !connection.source ||
        !connection.target
      ) {
        return;
      }

      const condition =
        connection.sourceHandle === "yes"
          ? "YES"
          : connection.sourceHandle === "no"
          ? "NO"
          : null;

      if (!condition) {
        return;
      }

      const newEdge: Edge = {
        id: `${connection.source}-${condition}-${connection.target}`,
        source: connection.source,
        target: connection.target,
        sourceHandle: connection.sourceHandle,
        label: condition,
        animated: false,
        style: {
          stroke:
            condition === "YES"
              ? "#22c55e"
              : "#ef4444",
          strokeWidth: 2,
        },
        labelStyle: {
          fontWeight: 700,
          fontSize: 12,
        },
        labelBgStyle: {
          fill: "#ffffff",
        },
      };

      setEdges((currentEdges) =>
        addEdge(newEdge, currentEdges)
      );
    },
    [setEdges]
  );

  // ==========================================================
  // ADD NODE
  // ==========================================================

  const addNode = () => {
    const id = String(nodeCounter);

    const newNode: Node = {
      id,
      type: "decision",
      position: {
        x: 150 + Math.random() * 500,
        y: 100 + Math.random() * 400,
      },
      data: {
        prompt: "Enter your decision question?",
      },
    };

    setNodes((currentNodes) => [
      ...currentNodes,
      newNode,
    ]);

    setNodeCounter(
      (counter) => counter + 1
    );
  };

  // ==========================================================
  // BUILD WORKFLOW PAYLOAD
  // ==========================================================

  const buildWorkflowPayload = () => {
    return {
      workflow: {
        nodes: nodes.map((node) => ({
          id: node.id,
          prompt: String(
            node.data?.prompt ?? ""
          ),
        })),

        edges: edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          condition:
            typeof edge.label === "string"
              ? edge.label
              : "",
        })),

        start_node: nodes[0]?.id,
      },

      user_input: userInput,
    };
  };

  // ==========================================================
  // RUN WORKFLOW
  // ==========================================================

  const runWorkflow = async () => {
    if (!userInput.trim()) {
      setError("Please enter some input.");
      return;
    }
  
    if (nodes.length === 0) {
      setError("Add at least one decision node.");
      return;
    }
  
    setIsRunning(true);
    setError("");
    setExecution([]);
  
    try {
      const payload = buildWorkflowPayload();
  
      const response = await fetch(
        "http://localhost:8000/execute",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );
  
      if (!response.ok) {
        throw new Error(
          `Backend error: ${response.status}`
        );
      }
  
      const data = await response.json();
  
      const eventId = data.event_id;
  
      // Poll Inngest result
      for (let i = 0; i < 30; i++) {
        await new Promise((resolve) =>
          setTimeout(resolve, 1000)
        );
  
        const resultResponse = await fetch(
          `http://localhost:8000/execute/${eventId}`
        );
  
        const result = await resultResponse.json();
  
        if (result.completed) {
          setExecution(result.execution);
          return;
        }
      }
  
      throw new Error(
        "Workflow timed out."
      );
    } catch (error) {
      console.error(error);
  
      setError(
        "Failed to execute workflow."
      );
    } finally {
      setIsRunning(false);
    }
  };
  // ==========================================================
  // EXECUTED EDGES
  // ==========================================================

  const executionEdges = useMemo(() => {
    return edges.map((edge) => {
      const sourceExecution =
        execution.find(
          (step) =>
            step.node_id ===
            edge.source
        );

      const edgeWasTaken =
        sourceExecution?.decision ===
        edge.label;

      return {
        ...edge,

        animated: Boolean(edgeWasTaken),

        style: {
          ...edge.style,
          stroke:
            edge.label === "YES"
              ? "#22c55e"
              : "#ef4444",
          strokeWidth:
            edgeWasTaken ? 4 : 2,
          opacity:
            execution.length === 0 ||
            edgeWasTaken
              ? 1
              : 0.5,
        },
      };
    });
  }, [edges, execution]);

  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "#f8fafc",
      }}
    >
      {/* ======================================================
          TOOLBAR
      ====================================================== */}

      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          zIndex: 100,
        }}
      >
        <button
          onClick={addNode}
          style={{
            padding: "10px 16px",
            borderRadius: 8,
            border: "none",
            background: "#111111",
            color: "#ffffff",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          + Add Decision
        </button>
      </div>

      {/* ======================================================
          WORKFLOW PANEL
      ====================================================== */}

      <div
        style={{
          position: "absolute",
          top: 20,
          right: 20,
          width: 320,
          maxHeight:
            "calc(100vh - 40px)",
          overflowY: "auto",
          zIndex: 100,
          background: "#ffffff",
          padding: 16,
          borderRadius: 12,
          border: "1px solid #ddd",
          boxShadow:
            "0 4px 20px rgba(0,0,0,0.08)",
        }}
      >
        <div
          style={{
            fontWeight: 700,
            fontSize: 18,
            marginBottom: 4,
          }}
        >
          FlowMind
        </div>

        <div
          style={{
            fontSize: 13,
            color: "#666",
            marginBottom: 16,
          }}
        >
          AI Decision Workflow
        </div>

        {/* ====================================================
            USER INPUT
        ==================================================== */}

        <div
          style={{
            fontWeight: 700,
            fontSize: 14,
            marginBottom: 8,
          }}
        >
          Test Input
        </div>

        <textarea
          value={userInput}
          onChange={(event) =>
            setUserInput(
              event.target.value
            )
          }
          placeholder="Enter user input..."
          style={{
            width: "100%",
            minHeight: 100,
            padding: 10,
            border:
              "1px solid #d1d5db",
            borderRadius: 8,
            resize: "vertical",
            boxSizing: "border-box",
            outline: "none",
            fontSize: 14,
          }}
        />

        {/* ====================================================
            RUN BUTTON
        ==================================================== */}

        <button
          onClick={runWorkflow}
          disabled={isRunning}
          style={{
            width: "100%",
            marginTop: 10,
            padding: "10px 16px",
            borderRadius: 8,
            border: "none",
            background: isRunning
              ? "#9ca3af"
              : "#111111",
            color: "#ffffff",
            cursor: isRunning
              ? "not-allowed"
              : "pointer",
            fontWeight: 600,
          }}
        >
          {isRunning
            ? "Running..."
            : "Run Workflow"}
        </button>

        {/* ====================================================
            ERROR
        ==================================================== */}

        {error && (
          <div
            style={{
              marginTop: 10,
              padding: 10,
              borderRadius: 8,
              background: "#fef2f2",
              color: "#dc2626",
              fontSize: 13,
            }}
          >
            {error}
          </div>
        )}

        {/* ====================================================
            EXECUTION LOG
        ==================================================== */}

        {execution.length > 0 && (
          <div
            style={{
              marginTop: 20,
            }}
          >
            <div
              style={{
                fontWeight: 700,
                marginBottom: 10,
              }}
            >
              Execution
            </div>

            {execution.map(
              (step, index) => (
                <div
                  key={`${step.node_id}-${index}`}
                  style={{
                    padding: 10,
                    marginBottom: 8,
                    borderRadius: 8,
                    background:
                      step.decision ===
                      "YES"
                        ? "#f0fdf4"
                        : "#fef2f2",
                    border:
                      step.decision ===
                      "YES"
                        ? "1px solid #86efac"
                        : "1px solid #fca5a5",
                    fontSize: 13,
                  }}
                >
                  <div
                    style={{
                      fontWeight: 700,
                    }}
                  >
                    Step {index + 1} —
                    Node{" "}
                    {step.node_id}
                  </div>

                  <div
                    style={{
                      marginTop: 4,
                    }}
                  >
                    Decision:{" "}
                    <strong>
                      {step.decision}
                    </strong>
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </div>

      {/* ======================================================
          REACT FLOW
      ====================================================== */}

      <ReactFlow
        nodes={nodesWithCallbacks}
        edges={executionEdges}
        nodeTypes={nodeTypes}
        onNodesChange={
          onNodesChange
        }
        onEdgesChange={
          onEdgesChange
        }
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}