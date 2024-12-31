"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchConvenios,
  startScraping,
  fetchCategories,
} from "@/services/convenioService";
import { debounce } from "@/utils/debouce";
import ScrapyProgress from "./components/ProgressMonitor";
import DiscountsTable from "./components/DiscountsTable";
import { useUrlQueryParams } from "./hooks/useUrlQueryParams";
import { useEffect, useRef, useState } from "react";

export default function HomePage() {
  const queryClient = useQueryClient();
  const { params, updateParams, clearParams } = useUrlQueryParams({
    defaultParams: {
      search: "",
      page: 1,
      pageSize: 10,
      sortBy: "date",
      order: "desc",
      category: "", // Adicionando categoria ao estado
    },
  });

  const searchRef = useRef<HTMLInputElement>(null);

  const { search, page, pageSize, sortBy, order, category } = params;
  const [isRunning, setIsRunning] = useState(false);

  const {
    data: conveniosData,
    isLoading: conveniosLoading,
    isError: conveniosError,
    error: conveniosErrorObj,
  } = useQuery({
    queryKey: ["convenios", search, page, pageSize, sortBy, order, category],
    queryFn: () =>
      fetchConvenios(search, page, pageSize, sortBy, order, category),
  });

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const scrapeMutation = useMutation({
    mutationFn: startScraping,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["convenios"] });
      queryClient.invalidateQueries({ queryKey: ["progress"] });
    },
  });

  const handleSearchChange = debounce((value: string) => {
    updateParams({ search: value, page: 1 });
  }, 300);

  const handleCategoryChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    updateParams({ category: event.target.value, page: 1 });
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      updateParams({ order: order === "asc" ? "desc" : "asc", page: 1 });
    } else {
      updateParams({ sortBy: field, order: "asc", page: 1 });
    }
  };

  useEffect(() => {
    if (searchRef.current) {
      searchRef.current.focus();
      if (search) {
        searchRef.current.value = search;
      }
    }
  }, [searchRef.current, search]);

  const totalPages = conveniosData?.total_pages || 1;

  if (conveniosError) {
    return (
      <div className="container mx-auto py-10">
        <p className="text-red-500">
          Erro: {(conveniosErrorObj as Error).message}
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      <div className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold mb-4">Lista de Convênios</h1>

        <button
          onClick={() => scrapeMutation.mutate()}
          className=" text-white px-4 py-2 rounded-lg"
          disabled={isRunning}
          style={{ cursor: isRunning ? "not-allowed" : "pointer" }}
        >
          {isRunning ? "🌐" : "🔄"}
        </button>
      </div>
      <div className="mb-4 flex gap-x-4">
        {/* Campo de busca */}
        <input
          type="text"
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Buscar convênios"
          className="border border-gray-300 rounded-lg px-4 py-2 w-full text-gray-800"
          ref={searchRef}
        />

        {/* Filtro de categorias */}
        <select
          onChange={handleCategoryChange}
          value={category}
          className="border border-gray-300 rounded-lg px-4 py-2 text-gray-800"
        >
          <option value="">Todas as categorias</option>
          {!categoriesLoading &&
            categories.map((cat: string) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
        </select>

        <button
          onClick={() => clearParams()}
          className="bg-red-500 text-white px-4 py-2 rounded-lg"
        >
          Limpar
        </button>
      </div>

      <ScrapyProgress isRunning={isRunning} setIsRunning={setIsRunning} />
      {isRunning ? null : conveniosLoading ? (
        <p>Carregando convênios...</p>
      ) : (
        <>
          <DiscountsTable
            convenios={conveniosData.data}
            sortBy={sortBy}
            order={order}
            onSort={handleSort}
          />
          <div className="flex justify-between items-center mt-4">
            <div></div>
            <div className="flex justify-center items-center mt-4 gap-x-4">
              <button
                onClick={() =>
                  updateParams({ page: Math.max(parseInt(page) - 1, 1) })
                }
                disabled={page === 1}
                className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-gray-600 px-4">
                Página {page} de {totalPages}
              </span>
              <button
                onClick={() =>
                  updateParams({
                    page: Math.min(parseInt(page) + 1, totalPages),
                  })
                }
                disabled={page === totalPages}
                className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg disabled:opacity-50"
              >
                Próxima
              </button>
            </div>
            <div className="flex justify-center items-center mt-4">
              {/* pagesize */}
              <select
                onChange={(e) =>
                  updateParams({ pageSize: +e.target.value, page: 1 })
                }
                value={pageSize}
                className="border border-gray-300 rounded-lg px-4 py-2 text-gray-800"
              >
                <option value="10">10 por página</option>
                <option value="20">20 por página</option>
                <option value="50">50 por página</option>
              </select>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
