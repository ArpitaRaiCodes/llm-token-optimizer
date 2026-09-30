import { useEffect, useState, useCallback, useRef } from "react";
import ModelSelector from "./components/ModelSelector.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import { getModels, countTokens, compressText } from "./api/client.js";

const DEFAULT_MODELS = [
  { id: "qwen2.5:0.5b", label: "Qwen2.5 0.5B", min_ram_gb: 2, available: false },
  { id: "qwen2.5:1.5b", label: "Qwen2.5 1.5B", min_ram_gb: 4, available: false },
  { id: "qwen2.5:3b", label: "Qwen2.5 3B", min_ram_gb: 6, available: false },
];

export default function App() {
  const [text, setText] = useState("");
  const [tokenCount, setTokenCount] = useState(0);
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [selectedModel, setSelectedModel] = useState("qwen2.5:0.5b");
  const [ollamaReachable, setOllamaReachable] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const debounceRef = useRef(null);

  useEffect(() => {
    getModels()
      .then((data) => {
        setModels(data.models);
        setOllamaReachable(data.ollama_reachable);
      })
      .catch(() => setOllamaReachable(false));
  }, []);

  // Debounced live token counting as the user types.
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!text) {
      setTokenCount(0);
      return;
    }
    debounceRef.current = setTimeout(() => {
      countTokens(text)
        .then((res) => setTokenCount(res.tokens))
        .catch(() => {});
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [text]);

  const handleMinimize = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await compressText(text, selectedModel);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [text, selectedModel]);

  const handleCopy = useCallback(() => {
    if (!result) return;
    navigator.clipboard.writeText(result.compressed_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [result]);

  const handleExport = useCallback(() => {
    if (!result) return;
    const md = `# Token Minimizer Export

**Model used:** ${result.model_used}
**Date:** ${new Date().toISOString()}
**Tokens saved:** ${result.tokens_saved} (${result.percent_saved}%)

## Original (${result.original_tokens} tokens)

${result.original_text}

## Compressed (${result.compressed_tokens} tokens)

${result.compressed_text}
`;
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `token-minimizer-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  return (
    <div className="app">
      <header>
        <h1>Token Minimizer</h1>
        <p className="subtitle">
          Shrink your prompts locally with Qwen — same meaning, fewer tokens.
        </p>
      </header>

      <main>
        <div className="input-section">
          <textarea
            className="text-input"
            placeholder="Paste your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
          />
          <div className="input-footer">
            <span className="token-badge">{tokenCount} tokens</span>
            <ModelSelector
              models={models}
              selected={selectedModel}
              onSelect={setSelectedModel}
              ollamaReachable={ollamaReachable}
            />
          </div>
          <button
            className="minimize-btn"
            onClick={handleMinimize}
            disabled={loading || !text.trim() || !ollamaReachable}
          >
            {loading ? "Minimizing..." : "Minimize token"}
          </button>
          {error && <p className="error">{error}</p>}
        </div>

        <ResultPanel
          result={result}
          onCopy={handleCopy}
          onExport={handleExport}
          copied={copied}
        />
      </main>
    </div>
  );
}
