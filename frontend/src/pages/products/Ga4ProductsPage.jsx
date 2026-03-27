import { useCallback } from 'react';
import { fetchGa4Products } from '../../lib/api/ga4';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function Ga4ProductsPage({ filters }) {
  const loader = useCallback(() => fetchGa4Products(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="GA4 Products"
      subtitle="Produse GA4 conectate la API-ul Python."
      chips={[
        `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
        filters.productFilter ? `Produs: ${filters.productFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload products"
      metricDefs={[
        { key: 'views', label: 'Views' },
        { key: 'add_to_cart', label: 'Add To Cart' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'revenue', label: 'Revenue' },
      ]}
      columns={[
        { key: 'item_name', label: 'Produs' },
        { key: 'item_id', label: 'Item ID' },
        { key: 'items_viewed', label: 'Views' },
        { key: 'items_added_to_cart', label: 'Add To Cart' },
        { key: 'items_purchased', label: 'Purchases' },
        { key: 'item_revenue', label: 'Revenue' },
        { key: 'cart_rate', label: 'Cart Rate %' },
        { key: 'purchase_rate', label: 'Purchase Rate %' },
      ]}
    />
  );
}
