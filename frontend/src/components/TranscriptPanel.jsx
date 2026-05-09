export function TranscriptPanel({ item }) {
  return (
    <section className="panel transcriptPanel">
      <div className="panelTitle">
        <span>Call Transcript</span>
        <strong>{item ? `urgency ${item.urgency_score.toFixed(3)}` : "--"}</strong>
      </div>
      {item ? (
        <>
          <p>{item.transcript}</p>
          <div className="chips">
            <span>{item.backend}</span>
            {item.matched_phrases?.slice(0, 4).map((phrase) => <span key={phrase}>{phrase}</span>)}
          </div>
        </>
      ) : (
        <div className="empty">Waiting for transcript events</div>
      )}
    </section>
  );
}
