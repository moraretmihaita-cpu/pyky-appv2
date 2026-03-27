import FilterGroup from '../ui/FilterGroup';

export const defaultFilters = {
  // Single period selector; we translate it into GA4/Google Ads/Meta params.
  periodPreset: 'LAST_30_DAYS',
  ga4Start: '30daysAgo',
  ga4End: 'today',
  adsDateRange: 'LAST_30_DAYS',
  metaDateRange: 'last_30d',
  campaignFilter: '',
  productFilter: '',
  selectedItemId: '',
  trafficType: 'toate',
  pageType: 'toate',
  sourceFilter: '',
  comparePrevious: false,
};

function isIsoDate(value) {
  return /^\d{4}-\d{2}-\d{2}$/.test(String(value || ''));
}

function toGa4DateStrFromDaysAgo(daysAgo) {
  const d = Number(daysAgo || 0);
  return d <= 0 ? 'today' : `${d}daysAgo`;
}

function isoToUTCDate(iso) {
  if (!isIsoDate(iso)) return null;
  const [y, m, d] = iso.split('-').map((x) => Number(x));
  return Date.UTC(y, m - 1, d);
}

function diffDaysUTC(dateUTC) {
  const today = new Date();
  const todayUTC = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  const targetUTC = dateUTC;
  return Math.max(0, Math.floor((todayUTC - targetUTC) / 86400000));
}

function startOfMonthUTC(year, monthIndex) {
  return Date.UTC(year, monthIndex, 1);
}

function endOfMonthUTC(year, monthIndex) {
  // Day 0 of next month is the last day of current month
  return Date.UTC(year, monthIndex + 1, 0);
}

function sameIsoDay(aUtc, bUtc) {
  return Number(aUtc) === Number(bUtc);
}

function inferAdsMetaFromCustomRange(ga4StartIso, ga4EndIso) {
  const startUTC = isoToUTCDate(ga4StartIso);
  const endUTC = isoToUTCDate(ga4EndIso);
  if (!startUTC || !endUTC) {
    return { adsDateRange: 'LAST_30_DAYS', metaDateRange: 'last_30d' };
  }

  const today = new Date();
  const todayUTC = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  const year = today.getUTCFullYear();
  const monthIndex = today.getUTCMonth();

  const thisMonthStartUTC = startOfMonthUTC(year, monthIndex);

  const prevYear = monthIndex === 0 ? year - 1 : year;
  const prevMonthIndex = monthIndex === 0 ? 11 : monthIndex - 1;
  const lastMonthStartUTC = startOfMonthUTC(prevYear, prevMonthIndex);
  const lastMonthEndUTC = endOfMonthUTC(prevYear, prevMonthIndex);

  // Match "this month" exactly (start of month -> today)
  if (sameIsoDay(startUTC, thisMonthStartUTC) && sameIsoDay(endUTC, todayUTC)) {
    return { adsDateRange: 'THIS_MONTH', metaDateRange: 'this_month' };
  }

  // Match "last month" exactly (start -> end of previous month)
  if (sameIsoDay(startUTC, lastMonthStartUTC) && sameIsoDay(endUTC, lastMonthEndUTC)) {
    return { adsDateRange: 'LAST_MONTH', metaDateRange: 'last_month' };
  }

  // Match rolling windows ending today
  const daysDiffToStart = diffDaysUTC(startUTC);
  const daysDiffToEnd = diffDaysUTC(endUTC);
  if (daysDiffToEnd === 0) {
    if (daysDiffToStart === 7) return { adsDateRange: 'LAST_7_DAYS', metaDateRange: 'last_7d' };
    if (daysDiffToStart === 30) return { adsDateRange: 'LAST_30_DAYS', metaDateRange: 'last_30d' };
  }

  return { adsDateRange: 'LAST_30_DAYS', metaDateRange: 'last_30d' };
}

function computeDerivedFilters(periodPreset) {
  const today = new Date();
  const year = today.getUTCFullYear();
  const monthIndex = today.getUTCMonth();

  if (periodPreset === 'LAST_7_DAYS') {
    const endDiff = 0;
    const startDiff = 7;
    return {
      ga4Start: toGa4DateStrFromDaysAgo(startDiff),
      ga4End: toGa4DateStrFromDaysAgo(endDiff),
      adsDateRange: 'LAST_7_DAYS',
      metaDateRange: 'last_7d',
    };
  }

  if (periodPreset === 'LAST_30_DAYS') {
    const endDiff = 0;
    const startDiff = 30;
    return {
      ga4Start: toGa4DateStrFromDaysAgo(startDiff),
      ga4End: toGa4DateStrFromDaysAgo(endDiff),
      adsDateRange: 'LAST_30_DAYS',
      metaDateRange: 'last_30d',
    };
  }

  if (periodPreset === 'THIS_MONTH') {
    const startUTC = startOfMonthUTC(year, monthIndex);
    const startDiff = diffDaysUTC(startUTC);
    return {
      ga4Start: toGa4DateStrFromDaysAgo(startDiff),
      ga4End: 'today',
      adsDateRange: 'THIS_MONTH',
      metaDateRange: 'this_month',
    };
  }

  if (periodPreset === 'LAST_MONTH') {
    const prevYear = monthIndex === 0 ? year - 1 : year;
    const prevMonthIndex = monthIndex === 0 ? 11 : monthIndex - 1;
    const startUTC = startOfMonthUTC(prevYear, prevMonthIndex);
    const endUTC = endOfMonthUTC(prevYear, prevMonthIndex);
    const startDiff = diffDaysUTC(startUTC);
    const endDiff = diffDaysUTC(endUTC);
    return {
      ga4Start: toGa4DateStrFromDaysAgo(startDiff),
      ga4End: toGa4DateStrFromDaysAgo(endDiff),
      adsDateRange: 'LAST_MONTH',
      metaDateRange: 'last_month',
    };
  }

  // Fallback to current defaults
  return {
    ga4Start: '30daysAgo',
    ga4End: 'today',
    adsDateRange: 'LAST_30_DAYS',
    metaDateRange: 'last_30d',
  };
}

export default function FiltersSidebar({ filters, onChange }) {
  const updateFilter = (key, value) => {
    onChange(key, value);
  };

  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">AI Ads Analyst</h1>
      <p className="sidebar-subtitle">Frontend consolidat pe client API unic.</p>

      <FilterGroup title="Perioade">
        <label className="label">Perioadă globală</label>
        <select
          className="select"
          value={filters.periodPreset}
          onChange={(e) => {
            const nextPreset = e.target.value;
            onChange('periodPreset', nextPreset);
            if (nextPreset !== 'CUSTOM_RANGE') {
              const derived = computeDerivedFilters(nextPreset);
              // Keep backward compatibility: other pages still read ga4Start/adsDateRange/metaDateRange.
              onChange('ga4Start', derived.ga4Start);
              onChange('ga4End', derived.ga4End);
              onChange('adsDateRange', derived.adsDateRange);
              onChange('metaDateRange', derived.metaDateRange);
            } else {
              // Default to last 30 days, but allow user to input exact GA4 dates.
              onChange('ga4Start', isIsoDate(filters.ga4Start) ? filters.ga4Start : '2026-01-01');
              onChange('ga4End', isIsoDate(filters.ga4End) ? filters.ga4End : '2026-01-31');
              onChange('adsDateRange', 'LAST_30_DAYS');
              onChange('metaDateRange', 'last_30d');
            }
          }}
        >
          <option value="LAST_7_DAYS">Last 7 days</option>
          <option value="LAST_30_DAYS">Last 30 days</option>
          <option value="THIS_MONTH">This month</option>
          <option value="LAST_MONTH">Last month</option>
          <option value="CUSTOM_RANGE">Custom range</option>
        </select>

        {filters.periodPreset === 'CUSTOM_RANGE' ? (
          <>
            <label className="label">Start date (GA4)</label>
            <input
              className="input"
              type="date"
              value={isIsoDate(filters.ga4Start) ? filters.ga4Start : ''}
              onChange={(e) => {
                const nextStart = e.target.value;
                onChange('ga4Start', nextStart);
                const derived = inferAdsMetaFromCustomRange(nextStart, filters.ga4End);
                onChange('adsDateRange', derived.adsDateRange);
                onChange('metaDateRange', derived.metaDateRange);
              }}
            />

            <label className="label">End date (GA4)</label>
            <input
              className="input"
              type="date"
              value={isIsoDate(filters.ga4End) ? filters.ga4End : ''}
              onChange={(e) => {
                const nextEnd = e.target.value;
                onChange('ga4End', nextEnd);
                const derived = inferAdsMetaFromCustomRange(filters.ga4Start, nextEnd);
                onChange('adsDateRange', derived.adsDateRange);
                onChange('metaDateRange', derived.metaDateRange);
              }}
            />
          </>
        ) : null}
      </FilterGroup>

      <FilterGroup title="Scope">
        <label className="label">Filtru nume campanie</label>
        <input
          className="input"
          value={filters.campaignFilter}
          onChange={(e) => updateFilter('campaignFilter', e.target.value)}
        />

        <label className="label">Filtru nume produs</label>
        <input
          className="input"
          value={filters.productFilter}
          onChange={(e) => updateFilter('productFilter', e.target.value)}
        />

        <label className="label">Selected item ID</label>
        <input
          className="input"
          value={filters.selectedItemId}
          onChange={(e) => updateFilter('selectedItemId', e.target.value)}
        />

        <label className="label">Traffic type</label>
        <select
          className="select"
          value={filters.trafficType}
          onChange={(e) => updateFilter('trafficType', e.target.value)}
        >
          <option>toate</option>
          <option>paid only</option>
          <option>google / cpc only</option>
        </select>

        <label className="label">Page type</label>
        <select
          className="select"
          value={filters.pageType}
          onChange={(e) => updateFilter('pageType', e.target.value)}
        >
          <option>toate</option>
          <option>produse (/p/)</option>
          <option>categorii (/c/)</option>
        </select>

        <label className="label">Source filter</label>
        <input
          className="input"
          value={filters.sourceFilter}
          onChange={(e) => updateFilter('sourceFilter', e.target.value)}
        />

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={!!filters.comparePrevious}
            onChange={(e) => updateFilter('comparePrevious', e.target.checked)}
          />
          <span>Compară cu perioada anterioară</span>
        </label>
      </FilterGroup>
    </aside>
  );
}
