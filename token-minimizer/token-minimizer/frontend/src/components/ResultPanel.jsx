export default function ResultPanel({ result, onCopy, onExport, copied }) {
  if (!result) return null;

  return (
    <div className="result-panel">
      <div className="stats-row">
        <div className="stat">
          <span className="stat-value">{result.original_tokens}</span>
          <span className="stat-label">original tokens</span>
        </div>
        <div className="stat arrow">→</div>
        <div className="stat">
          <span className="stat-value">{result.compressed_tokens}</span>
          <span className="stat-label">compressed tokens</span>
        </div>
        <div className="stat highlight">
          <span className="stat-value">{result.percent_saved}%</span>
          <span className="stat-label">saved</span>
        </div>
      </div>

      <textarea readOnly value={result.compressed_text} className="result-text" />

      <div className="button-row">
        <button onClick={onCopy}>{copied ? "Copied!" : "Copy text"}</button>
        <button onClick={onExport} className="secondary">
          Export as .md
        </button>
      </div>
    </div>
  );
}
