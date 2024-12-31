import axios from "axios";

const API_URL = "http://127.0.0.1:5001";

export const fetchConvenios = async (
  search: string,
  page: number,
  page_size: number,
  sort_by: string,
  order: string,
  category?: string
) => {
  const response = await axios.get(`${API_URL}/convenios`, {
    params: { search, page, page_size, sort_by, order, category },
  });
  return response.data;
};

export const startScraping = async () => {
  const response = await axios.post(`${API_URL}/scrape`);
  return response.data;
};

export async function fetchConvenioById(id: string) {
  const response = await axios.get(`${API_URL}/convenio/${id}`);
  return response.data;
}

export async function fetchConveniosByCategory(cat: string) {
  const response = await axios.get(`${API_URL}/convenios_by_cat/${cat}`);
  return response.data;
}

export const fetchCategories = async () => {
  const response = await axios.get(`${API_URL}/get_categories`);
  return response.data;
};
