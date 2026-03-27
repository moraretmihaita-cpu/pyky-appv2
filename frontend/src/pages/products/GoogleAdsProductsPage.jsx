import { useCallback } from 'react';
import { fetchGoogleAdsProducts } from '../../lib/api/googleAds';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function GoogleAdsProductsPage({ filters }) {
  const loader = useCallback(() => fetchGoogleAdsProducts(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Google Ads Products"
      subtitle="Produse Google Ads conectate la API-ul Python."
      chips={[
        `Ads: ${filters.adsDateRange}`,
        filters.productFilter ? `Produs: ${filters.productFilter}` : null,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload products"
      metricDefs={[
        { key: 'cost', label: 'Cost' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'conversions', label: 'Conversions' },
        { key: 'value', label: 'Value' },
      ]}
      columns={[
        { key: 'product_item_id', label: 'Item ID' },
        { key: 'product_title', label: 'Produs' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'impressions', label: 'Impresii' },
        { key: 'cost', label: 'Cost' },
        { key: 'conversions', label: 'Conversions' },
        { key: 'conversion_value', label: 'Value' },
        { key: 'ctr', label: 'CTR %' },
        { key: 'cpc', label: 'CPC' },
        { key: 'roas', label: 'ROAS' },
      ]}
    />
  );
}
