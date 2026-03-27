export default function ErrorBox({ error }) {
  if (!error) return null;

  return (
    <div className="card panel" style={{ color: '#fca5a5' }}>
      {error}
    </div>
  );
}
