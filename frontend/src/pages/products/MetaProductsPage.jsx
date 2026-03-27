import { useCallback } from 'react';
import { fetchMetaProducts } from '../../lib/api/meta';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function MetaProductsPage({ filters }) {
  const loader = useCallback(() => fetchMetaProducts(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Meta Products"
      subtitle="Produse Meta conectate la API-ul Python."
      chips={[
        `Meta: ${filters.metaDateRange}`,
        filters.productFilter ? `Produs: ${filters.productFilter}` : null,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload products"
      metricDefs={[
        { key: 'spend', label: 'Spend' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'value', label: 'Value' },
      ]}
      columns={[
        { key: 'product_id', label: 'Item ID' },
        { key: 'product_name', label: 'Produs' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'impressions', label: 'Impresii' },
        { key: 'spend', label: 'Spend' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'purchase_value', label: 'Value' },
        { key: 'ctr', label: 'CTR %' },
        { key: 'cpc', label: 'CPC' },
        { key: 'roas', label: 'ROAS' },
      ]}
    />
  );
}
