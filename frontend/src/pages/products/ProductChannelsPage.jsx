import { useCallback } from 'react';
import { fetchGa4ProductChannels } from '../../lib/api/ga4';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function ProductChannelsPage({ filters }) {
  const loader = useCallback(() => fetchGa4ProductChannels(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Product Channels"
      subtitle="Canale GA4 la nivel de produs."
      chips={[
        `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
        filters.sourceFilter ? `Source: ${filters.sourceFilter}` : null,
        filters.productFilter ? `Produs: ${filters.productFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload product channels"
      metricDefs={[
        { key: 'views', label: 'Views' },
        { key: 'add_to_cart', label: 'Add To Cart' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'revenue', label: 'Revenue' },
      ]}
      columns={[
        { key: 'item_name', label: 'Produs' },
        { key: 'item_id', label: 'Item ID' },
        { key: 'source_medium', label: 'Source / Medium' },
        { key: 'items_viewed', label: 'Views' },
        { key: 'items_added_to_cart', label: 'Add To Cart' },
        { key: 'items_purchased', label: 'Purchases' },
        { key: 'item_revenue', label: 'Revenue' },
      ]}
    />
  );
}
