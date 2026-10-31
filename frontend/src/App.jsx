import { useEffect, useRef, useState } from "react";

const API = import.meta.env.VITE_API_URL || "";

const LANGUAGES = {
  auto: "Auto detect",
  en: "English",
  te: "తెలుగు - Telugu",
  hi: "हिन्दी - Hindi",
};

const LANG_NAMES = { en: "English", te: "Telugu", hi: "Hindi" };

function scoreColor(score) {
  if (score >= 0.6) return "#2f8a4f";
  if (score >= 0.45) return "#b7791f";
  return "#b42318";
}

// PDF tables arrive flattened ("1 Crop Cotton 2 Variety ..."). Put a comma
// before each numbered field so the snippet is readable.
function formatSnippet(text) {
  return (text || "").replace(/\s(\d{1,2})\s(?=[A-Z])/g, ", $1 ").trim();
}

// Show **bold** properly and drop stray markdown asterisks.
function renderAnswerLine(text, lineIndex) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, partIndex) => {
    const key = `${lineIndex}-${partIndex}`;
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }
    return part.replace(/\*/g, "");
  });
}

function renderAnswer(text) {
  return (text || "")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => (
      <p className="answer-item" key={index}>
        {renderAnswerLine(line.replace(/^\s*[-*]\s+/, ""), index)}
      </p>
    ));
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [voiceState, setVoiceState] = useState("idle"); // idle | loading | playing
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const audioRef = useRef(null);
  const speakToken = useRef(0);
  const speechCache = useRef({ key: "", promise: null });

  function stopSpeech() {
    speakToken.current += 1;
    window.speechSynthesis?.cancel();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    setVoiceState("idle");
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
    return () => stopSpeech();
  }, []);

  // Fetch the voice once and keep it, so Play is instant after prefetch.
  function fetchSpeech(text, lang) {
    const voiceLang = lang === "hi" || lang === "te" ? lang : "en";
    const key = `${voiceLang}|${text}`;
    if (speechCache.current.key === key && speechCache.current.promise) {
      return speechCache.current.promise;
    }
    const promise = fetch(`${API}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language: voiceLang }),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Voice could not be generated.");
        return response.blob();
      })
      .then((blob) => URL.createObjectURL(blob));
    promise.catch(() => {
      if (speechCache.current.promise === promise) {
        speechCache.current = { key: "", promise: null };
      }
    });
    speechCache.current = { key, promise };
    return promise;
  }

  async function speakAnswer(text, lang) {
    if (!text) return;
    stopSpeech();
    const myToken = speakToken.current;
    try {
      setVoiceState("loading");
      const url = await fetchSpeech(text, lang);
      if (myToken !== speakToken.current) return; // newer click or Stop happened
      const audio = new Audio(url);
      audio.onended = () => setVoiceState("idle");
      audioRef.current = audio;
      await audio.play();
      setVoiceState("playing");
    } catch (err) {
      setVoiceState("idle");
      setError(err.message || "Voice playback failed.");
    }
  }

  // Prepare the voice in the background as soon as an answer appears.
  useEffect(() => {
    if (!result) return;
    fetchSpeech(result.speech_text || result.final_answer, result.language || "en").catch(() => {});
  }, [result]);

  async function submitText(event) {
    event.preventDefault();
    if (!question.trim()) return;
    stopSpeech();
    setLoading(true);
    setError("");
    setMessage("");
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
    setMessage("");
    stopSpeech();
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setError("Audio recording is not supported in this browser. Try Chrome or Edge.");
      return;
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      setError(
        err.name === "NotAllowedError"
          ? "Microphone permission was denied."
          : "Unable to access the microphone.",
      );
      return;
    }
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
      setMessage("Transcribing and verifying your question...");
      try {
        const response = await fetch(`${API}/voice`, { method: "POST", body: form });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Voice query failed");
        setQuestion(data.transcript || data.question);
        setResult(data);
        setMessage("");
        loadHistory();
      } catch (err) {
        setError(err.message);
        setMessage("");
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

  function clearAll() {
    stopSpeech();
    if (recording) stopRecording();
    setQuestion("");
    setResult(null);
    setError("");
    setMessage("");
  }

  const score = result ? Number(result.trust_score) : 0;
  const passed = result?.verdict === "PASS";

  return (
    <div className="agri-app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-logo">AG</span>
          <span>
            <b>AgriVerify</b>
            <small>Verified Agricultural Advisory</small>
          </span>
        </div>
        <span className="online">
          <i /> VVIT · AIM-C10
        </span>
      </header>

      <main>
        <section className="hero">
          <div>
            <p className="eyebrow">VOICE-BASED · MULTILINGUAL · VERIFIED</p>
            <h1>
              Farming advice you can <em>trust, with proof.</em>
            </h1>
            <p>
              Ask by typing or speaking in Telugu, Hindi or English. Every answer is
              checked against official Package of Practices documents and shown with a
              Trust Score and its sources.
            </p>
            <div className="hero-tags">
              <span>Multilingual voice</span>
              <span>Trust Score (τ ≥ 0.6)</span>
              <span>Source citations</span>
            </div>
          </div>
        </section>

        <div className="workspace">
          <section className="panel">
            <div className="panel-heading">
              <span>1</span>
              <div>
                <h2>Ask your question</h2>
                <p>Type it, or record your voice.</p>
              </div>
            </div>
            <form onSubmit={submitText}>
              <label htmlFor="language">Response language</label>
              <select
                id="language"
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                disabled={loading || recording}
              >
                {Object.entries(LANGUAGES).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>

              <div className="label-row">
                <label htmlFor="question">Your farming question</label>
                <small>{question.length}/2000</small>
              </div>
              <textarea
                id="question"
                rows="6"
                maxLength={2000}
                value={question}
                disabled={loading}
                onChange={(event) => {
                  setQuestion(event.target.value);
                  setError("");
                }}
                placeholder="What are the cotton varieties?  /  vari rakalu emiti?"
              />

              {!recording ? (
                <button type="button" className="mic-button" onClick={startRecording} disabled={loading}>
                  Record voice question
                </button>
              ) : (
                <button type="button" className="mic-button recording" onClick={stopRecording}>
                  Stop recording
                </button>
              )}

              <div className="actions">
                <button type="button" className="clear" onClick={clearAll}>
                  Clear
                </button>
                <button className="submit" type="submit" disabled={loading || !question.trim()}>
                  {loading ? "Working (about 10-20 s)..." : "Get verified answer"}
                </button>
              </div>
            </form>
            {message ? <p className="message">{message}</p> : null}
            {error ? (
              <p className="error" role="alert">
                {error}
              </p>
            ) : null}
          </section>

          <section className="panel">
            <div className="panel-heading">
              <span>2</span>
              <div>
                <h2>Verified advisory</h2>
                <p>Answer, Trust Score and sources.</p>
              </div>
              {result ? (
                <b className={`badge ${passed ? "pass" : "reject"}`}>{result.verdict}</b>
              ) : null}
            </div>

            {!result && !loading ? (
              <div className="empty">
                <h3>Your answer will appear here</h3>
                <p>Ask a question to get an answer checked against official documents.</p>
                <div>
                  <span>
                    01
                    <br />
                    <small>Retrieve</small>
                  </span>
                  <span>
                    02
                    <br />
                    <small>Generate</small>
                  </span>
                  <span>
                    03
                    <br />
                    <small>Verify</small>
                  </span>
                </div>
              </div>
            ) : null}

            {loading ? (
              <div className="empty">
                <div className="spinner" />
                <h3>Preparing your advice...</h3>
                <p>Retrieving documents, generating and verifying the answer.</p>
              </div>
            ) : null}

            {result && !loading ? (
              <div>
                <div className="trust-row">
                  <span>Trust Score</span>
                  <strong style={{ color: scoreColor(score) }}>{score.toFixed(4)}</strong>
                  <small>threshold {result.tau ?? 0.6}</small>
                </div>
                <div className="meter">
                  <div
                    className="meter-fill"
                    style={{
                      width: `${Math.max(4, Math.min(100, score * 100))}%`,
                      background: scoreColor(score),
                    }}
                  />
                </div>

                {result.search_query ? (
                  <p className="understood">
                    Understood as: <em>{result.search_query}</em>
                    {result.language ? ` · ${LANG_NAMES[result.language] || result.language}` : ""}
                  </p>
                ) : null}

                <div className="answer-tools">
                  <small>Answer</small>
                  <span>
                    <button type="button" onClick={() => navigator.clipboard?.writeText(result.final_answer)}>
                      Copy
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        speakAnswer(result.speech_text || result.final_answer, result.language || "en")
                      }
                    >
                      {voiceState === "loading" ? "Preparing voice..." : "Play voice"}
                    </button>
                    <button type="button" className="stop-reading" onClick={stopSpeech} disabled={voiceState === "idle"}>
                      Stop
                    </button>
                  </span>
                </div>
                <div className="answer-text">{renderAnswer(result.final_answer)}</div>

                {result.language && result.language !== "en" && result.generated_answer ? (
                  <details className="draft english-original">
                    <summary>English original (the text that was verified)</summary>
                    <p>{result.generated_answer}</p>
                  </details>
                ) : null}

                {result.verdict === "REJECT" && result.generated_answer ? (
                  <details className="draft">
                    <summary>Hidden unverified draft</summary>
                    <p>{result.generated_answer}</p>
                  </details>
                ) : null}

                <div className="sources">
                  <h3>
                    Supporting sources <small>{(result.sources || []).slice(0, 4).length} sources</small>
                  </h3>
                  {(result.sources || []).slice(0, 4).map((source, index) => (
                    <details key={`${source.file}-${index}`} className="source">
                      <summary>
                        <b>
                          {source.file} · p.{source.page}
                        </b>
                        <span>{formatSnippet(source.snippet).slice(0, 150)}...</span>
                      </summary>
                      <p>{formatSnippet(source.snippet)}</p>
                    </details>
                  ))}
                </div>
                <p className="disclaimer">
                  Informational guidance from official documents. Confirm important
                  treatment decisions with a local agricultural officer.
                </p>
              </div>
            ) : null}
          </section>
        </div>

        <section className="panel history-panel">
          <div className="panel-heading">
            <span>H</span>
            <div>
              <h2>Recent queries</h2>
              <p>Saved in the local database.</p>
            </div>
          </div>
          {history.length === 0 ? (
            <p className="muted">No history yet.</p>
          ) : (
            <ul className="history">
              {history.map((item) => (
                <li key={item.id}>
                  <strong>{item.question}</strong>
                  <span className={`pill ${item.verdict === "PASS" ? "pass" : "reject"}`}>
                    {item.verdict} · {item.trust_score} · {item.language}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer>Voice-Based Multilingual Agricultural Advisory · RAG with answer verification</footer>
    </div>
  );
}
