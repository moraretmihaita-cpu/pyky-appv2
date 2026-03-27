import { useMemo, useState } from 'react';

function normalize(value) {
  if (value === null || value === undefined) return '';
  return String(value).toLowerCase();
}

function isNumericLike(value) {
  if (value === null || value === undefined || value === '') return false;
  const str = String(value).trim().replace(',', '.');
  return /^-?\d+(?:\.\d+)?$/.test(str);
}

function toComparableNumber(value) {
  const str = String(value).trim().replace(',', '.');
  const num = Number(str);
  return Number.isFinite(num) ? num : null;
}

function matchesFilter(cellValue, filterValue) {
  const rawFilter = String(filterValue ?? '').trim();
  if (!rawFilter) return true;

  const exactMode = rawFilter.startsWith('=');
  const effectiveFilter = exactMode ? rawFilter.slice(1).trim() : rawFilter;

  if (isNumericLike(effectiveFilter) && isNumericLike(cellValue)) {
    const filterNum = toComparableNumber(effectiveFilter);
    const cellNum = toComparableNumber(cellValue);
    if (filterNum === null || cellNum === null) return false;
    return cellNum === filterNum;
  }

  if (exactMode) {
    return normalize(cellValue) === normalize(effectiveFilter);
  }

  return normalize(cellValue).includes(normalize(effectiveFilter));
}

export default function DataTable({ title, rows = [], columns = [] }) {
  const [sortKey, setSortKey] = useState(columns[0]?.key || '');
  const [sortDir, setSortDir] = useState('desc');
  const [filters, setFilters] = useState({});

  const visibleRows = useMemo(() => {
    let result = [...rows];

    result = result.filter((row) =>
      columns.every((column) => matchesFilter(row[column.key], filters[column.key]))
    );

    if (sortKey) {
      result.sort((a, b) => {
        const av = a?.[sortKey];
        const bv = b?.[sortKey];

        const aNum = typeof av === 'number' ? av : Number(av);
        const bNum = typeof bv === 'number' ? bv : Number(bv);
        const bothNumeric = !Number.isNaN(aNum) && !Number.isNaN(bNum);

        let comparison = 0;
        if (bothNumeric) {
          comparison = aNum - bNum;
        } else {
          comparison = normalize(av).localeCompare(normalize(bv));
        }

        return sortDir === 'asc' ? comparison : -comparison;
      });
    }

    return result;
  }, [rows, columns, filters, sortKey, sortDir]);

  const onSort = (key) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
      return;
    }
    setSortKey(key);
    setSortDir('desc');
  };

  return (
    <div className="card panel">
      <h3 className="section-title">{title}</h3>
      {rows.length === 0 ? (
        <div className="table-placeholder">Nu există date.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    onClick={() => onSort(column.key)}
                    style={{
                      textAlign: 'left',
                      padding: '10px 8px',
                      color: '#93a4bd',
                      borderBottom: '1px solid rgba(148,163,184,0.16)',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      userSelect: 'none',
                    }}
                  >
                    {column.label}{sortKey === column.key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : ''}
                  </th>
                ))}
              </tr>
              <tr>
                {columns.map((column) => (
                  <th key={column.key} style={{ padding: '8px' }}>
                    <input
                      value={filters[column.key] || ''}
                      onChange={(e) => setFilters((prev) => ({ ...prev, [column.key]: e.target.value }))}
                      placeholder={`Filtru ${column.label}`}
                      title="Text = căutare parțială. Numere = potrivire exactă. Pentru text exact, începe cu ="
                      style={{
                        width: '100%',
                        background: 'rgba(255,255,255,0.03)',
                        border: '1px solid rgba(148,163,184,0.26)',
                        borderRadius: 10,
                        color: '#e5ecf6',
                        padding: '8px 10px',
                        fontSize: 13,
                      }}
                    />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visibleRows.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      style={{
                        padding: '10px 8px',
                        borderBottom: '1px solid rgba(148,163,184,0.08)',
                        whiteSpace: 'nowrap',
                        verticalAlign: 'top',
                      }}
                    >
                      {row[column.key] ?? '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
