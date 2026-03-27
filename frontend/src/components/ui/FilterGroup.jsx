export default function FilterGroup({ title, children }) {
  return (
    <div className="card filter-group">
      <h3 className="filter-group-title">{title}</h3>
      {children}
    </div>
  );
}
