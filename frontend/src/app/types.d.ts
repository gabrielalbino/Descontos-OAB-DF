interface Convenio {
  id: number;
  title: string;
  cats: string;
  date: string;
  url: string;
  image: string;
  title_highlight: string;
  content_highlight: string;
  discounts_highlight: string;
  discounts: string;
}

interface ProgressData {
  pages_crawled: number;
  items_scraped: number;
  finished: boolean;
  scraping_in_progress: boolean;
  error: string | null;
}
