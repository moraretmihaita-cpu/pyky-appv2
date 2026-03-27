export default function SectionHeader({ title, subtitle, chips = [] }) {
  return (
    <>
      <div className="card section-card">
        <h2 className="section-title">{title}</h2>
        <p className="section-subtitle">{subtitle}</p>
      </div>

      <div className="chips">
        {chips
          .filter(Boolean)
          .map((chip) => (
            <div className="chip" key={chip}>
              {chip}
            </div>
          ))}
      </div>
    </>
  );
}
