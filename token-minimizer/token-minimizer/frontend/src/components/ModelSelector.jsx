export default function ModelSelector({ models, selected, onSelect, ollamaReachable }) {
  return (
    <div className="model-selector">
      <label htmlFor="model-select">Model</label>
      <select
        id="model-select"
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        disabled={!ollamaReachable}
      >
        {models.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label} {m.available ? "" : "(not pulled)"} — ~{m.min_ram_gb}GB RAM
          </option>
        ))}
      </select>
      {!ollamaReachable && (
        <p className="warning">
          Ollama isn't reachable. Run <code>ollama serve</code> and pull a model.
        </p>
      )}
    </div>
  );
}
