// src/services/progressService.ts
import axios from "axios";

const API_URL = "http://127.0.0.1:5001";

export interface ProgressData {
  pages_crawled: number;
  items_scraped: number;
  finished: boolean;
  error: string | null;
  scraping_in_progress: boolean;
}

export async function fetchProgress(): Promise<ProgressData> {
  const response = await axios.get(`${API_URL}/progress`);
  return response.data;
}
