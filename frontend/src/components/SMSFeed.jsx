export function SMSFeed({ items }) {
  return (
    <section className="panel smsPanel">
      <div className="panelTitle">
        <span>SMS Threat Feed</span>
        <strong>{items.length}</strong>
      </div>
      <div className="smsList">
        {items.length === 0 && <div className="empty">Waiting for SMS events</div>}
        {items.map((item, index) => (
          <article className="smsItem" key={`${item.timestamp}-${index}`}>
            <div className="smsScore">score {item.sms_score.toFixed(3)}</div>
            <p>{item.text_preview}</p>
            <div className="chips">
              {item.ml_source && <span>{item.ml_source}</span>}
              {item.scam_type && <span>{item.scam_type}</span>}
              {item.matched_rules?.slice(0, 3).map((rule) => <span key={rule}>{rule}</span>)}
              {item.url_flags?.slice(0, 3).map((flag) => <span key={flag}>{flag}</span>)}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
