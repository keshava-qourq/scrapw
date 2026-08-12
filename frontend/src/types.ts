export interface WatchlistItem {
  id: string;
  product_name: string;
  group_key: string;
  marketplace: string;
  price: number;
  rating: number | null;
  url: string;
  notes: string | null;
  created_at: string;
}

export interface WatchlistGroup {
  group_key: string;
  product_name: string;
  items: WatchlistItem[];
  lowest_price_item_id: string | null;
  highest_rated_item_id: string | null;
}

export interface WatchlistItemCreate {
  product_name: string;
  marketplace: string;
  price: number;
  rating?: number;
  url: string;
  notes?: string;
}

export type LiveMarketplace = "AMAZON" | "FLIPKART" | "MYNTRA" | "AJIO" | "OTHER";
export const LIVE_MARKETPLACES: LiveMarketplace[] = ["AMAZON", "FLIPKART", "MYNTRA", "AJIO", "OTHER"];
export type LiveAvailability = "IN_STOCK" | "OUT_OF_STOCK" | "UNKNOWN";
export type LiveSortOption = "relevance" | "price_low_to_high" | "price_high_to_low" | "rating" | "discount";

export interface LiveProduct {
  id: string;
  title: string;
  brand: string | null;
  marketplace: LiveMarketplace;
  seller: string | null;
  price: number | null;
  original_price: number | null;
  discount_percentage: number | null;
  currency: string;
  rating: number | null;
  review_count: number | null;
  image_url: string | null;
  product_url: string;
  availability: LiveAvailability;
  category: string | null;
  source: string;
  duplicate_group: string | null;
  duplicate_confidence: number | null;
  effective_price: number | null;
  applied_offer: string | null;
}

export type CardType = "credit" | "debit";

export interface Card {
  id: string;
  bank_name: string;
  card_name: string;
  card_type: CardType;
  network: string | null;
  created_at: string;
}

export interface CardCreate {
  bank_name: string;
  card_name: string;
  card_type: CardType;
  network?: string;
}

export interface ParsedQuery {
  keywords: string[];
  brand: string | null;
  category: string | null;
  max_price: number | null;
  min_price: number | null;
}

export interface LiveSearchResponse {
  query: string;
  parsed_query: ParsedQuery;
  total: number;
  page: number;
  limit: number;
  results: LiveProduct[];
  marketplace_status: Record<string, string>;
  cache_hit: boolean;
}

export const LIVE_SORT_OPTIONS: { value: LiveSortOption; label: string }[] = [
  { value: "relevance", label: "Relevance" },
  { value: "price_low_to_high", label: "Price: Low to High" },
  { value: "price_high_to_low", label: "Price: High to Low" },
  { value: "rating", label: "Rating" },
  { value: "discount", label: "Discount" },
];
