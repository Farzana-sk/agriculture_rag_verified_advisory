import { useEffect, useRef, useState } from "react";

const API = import.meta.env.VITE_API_URL || "";

function scoreColor(score) {
  if (score >= 0.6) return "#1f7a4d";
  if (score >= 0.45) return "#b7791f";
  return "#b42318";
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const audioRef = useRef(null);

  function stopSpeech() {
    window.speechSynthesis?.cancel();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
  }

  async function loadHistory() {
    try {
      const response = await fetch(`${API}/history`);
      const data = await response.json();
      setHistory(data.items || []);
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function speakAnswer(text, lang) {
    if (!text) return;
    stopSpeech();
    const voiceLang = lang === "hi" || lang === "te" ? lang : "en";
    const response = await fetch(`${API}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language: voiceLang }),
    });
    if (!response.ok) return;
    const blob = await response.blob();
    const audio = new Audio(URL.createObjectURL(blob));
    audioRef.current = audio;
    await audio.play();
  }

  async function submitText(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: question,
          language: language === "auto" ? null : language,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Query failed");
      setResult(data);
      loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function startRecording() {
    setError("");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
      const form = new FormData();
      form.append("file", blob, "farmer_question.webm");
      if (language !== "auto") form.append("language", language);
      setLoading(true);
      try {
        const response = await fetch(`${API}/voice`, { method: "POST", body: form });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Voice query failed");
        setQuestion(data.transcript || data.question);
        setResult(data);
        loadHistory();
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    mediaRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  function stopRecording() {
    mediaRef.current?.stop();
    setRecording(false);
  }

  return (
    <div className="page">
      <header>
        <p className="eyebrow">VVIT · AIM-C10 · Verified RAG Advisory</p>
        <h1>Voice-Based Agricultural Advisory</h1>
        <p className="lede">
          Ask in Telugu, Hindi, or English. The answer is written and spoken in
          the same language as the question. Use Auto detect, or set Telugu
          before recording a Telugu voice question.
        </p>
      </header>

      <form className="card" onSubmit={submitText}>
        <label htmlFor="language">Language</label>
        <select
          id="language"
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
        >
          <option value="auto">Auto detect</option>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="te">Telugu</option>
        </select>

        <label htmlFor="question">Farmer question</label>
        <textarea
          id="question"
          rows="4"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="ఉదాహరణ: vari rakalu emiti?  /  What are the cotton varieties?"
        />

        <div className="actions">
          <button type="submit" disabled={loading}>
            {loading ? "Working (about 10-20s)..." : "Get verified answer"}
          </button>
          {!recording ? (
            <button type="button" className="secondary" onClick={startRecording} disabled={loading}>
              Record voice
            </button>
          ) : (
            <button type="button" className="danger" onClick={stopRecording}>
              Stop recording
            </button>
          )}
        </div>
        {error ? <p className="error">{error}</p> : null}
      </form>

      {result ? (
        <section className="card result">
          <div className="result-top">
            <span className={`badge ${result.verdict === "PASS" ? "pass" : "reject"}`}>
              {result.verdict}
            </span>
            <strong style={{ color: scoreColor(result.trust_score) }}>
              Trust score {result.trust_score}
            </strong>
          </div>
          <div className="meter">
            <div
              className="meter-fill"
              style={{
                width: `${Math.max(4, Math.min(100, result.trust_score * 100))}%`,
                background: scoreColor(result.trust_score),
              }}
            />
          </div>
          <h2>Verified answer</h2>
          {result.search_query ? (
            <p className="lede">Understood as: {result.search_query}</p>
          ) : null}
          <p>{result.final_answer}</p>
          <div className="actions">
            <button
              type="button"
              className="secondary"
              onClick={() => speakAnswer(result.speech_text || result.final_answer, result.language || "en")}
            >
              Play voice
            </button>
            <button type="button" className="danger" onClick={stopSpeech}>
              Stop voice
            </button>
          </div>
          {result.verdict === "REJECT" && result.generated_answer ? (
            <details>
              <summary>Hidden unverified draft</summary>
              <p>{result.generated_answer}</p>
            </details>
          ) : null}
          <h3>Supporting sources</h3>
          <ul>
            {(result.sources || []).slice(0, 4).map((source, index) => (
              <li key={`${source.file}-${index}`}>
                <strong>
                  {source.file} · p.{source.page}
                </strong>
                <p>{source.snippet}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="card">
        <h2>Recent queries</h2>
        {history.length === 0 ? (
          <p>No history yet.</p>
        ) : (
          <ul className="history">
            {history.map((item) => (
              <li key={item.id}>
                <div>
                  <strong>{item.question}</strong>
                  <p>
                    {item.verdict} · {item.trust_score} · {item.language}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
