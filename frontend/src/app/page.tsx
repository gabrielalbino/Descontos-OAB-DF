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
import { Button } from "@/components/ui/button";
import { Eraser, RefreshCcw, RefreshCcwDot } from "lucide-react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";

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

  return (
    <div className="container mx-auto py-10">
      <div className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold mb-4">Lista de Convênios</h1>

        <Button
          variant="outline"
          disabled={isRunning}
          onClick={() => scrapeMutation.mutate()}
        >
          {isRunning ? <RefreshCcwDot size={16} /> : <RefreshCcw size={16} />}
          {isRunning ? "Atualizando..." : "Atualizar convênios"}
        </Button>
      </div>
      <div className="mb-4 flex gap-x-4">
        {/* Campo de busca */}
        <Input
          type="text"
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Buscar convênios"
          className="border border-gray-300 rounded-lg px-4 py-2 w-full text-gray-800"
          ref={searchRef}
        />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              {category ? category : "Todas as categorias"}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem
              onSelect={() => updateParams({ category: "", page: 1 })}
            >
              Todas as categorias
            </DropdownMenuItem>
            {!categoriesLoading &&
              categories.map((cat: string) => (
                <DropdownMenuItem
                  key={cat}
                  onSelect={() => updateParams({ category: cat, page: 1 })}
                >
                  {cat}
                </DropdownMenuItem>
              ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant="destructive" onClick={() => clearParams()}>
          <Eraser size={16} />
          Limpar filtros
        </Button>
      </div>
      <ScrapyProgress isRunning={isRunning} setIsRunning={setIsRunning} />
      {isRunning ? null : conveniosLoading ? (
        <p>Carregando convênios...</p>
      ) : conveniosError ? (
        <p>
          Erro ao carregar os convênios, Tente
          <a
            onClick={(e) => {
              e.preventDefault();
              scrapeMutation.mutate();
            }}
            href="#"
            className="text-blue-600"
          >
            {" "}
            atualizar
          </a>{" "}
          os convênios
        </p>
      ) : (
        <>
          <DiscountsTable
            convenios={conveniosData?.data}
            sortBy={sortBy}
            order={order}
            onSort={handleSort}
          />
          <div className="flex justify-between items-center mt-4">
            <div></div>
            <div className="flex justify-center items-center mt-4 gap-x-4">
              {/* <button
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
              </button> */}
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() =>
                        updateParams({ page: Math.max(parseInt(page) - 1, 1) })
                      }
                    />
                  </PaginationItem>
                  {/* <PaginationItem>
                    <PaginationLink href="#">1</PaginationLink>
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationLink href="#" isActive>
                      2
                    </PaginationLink>
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationLink href="#">3</PaginationLink>
                  </PaginationItem> */}
                  {[...Array(totalPages).keys()]
                    .filter((i) => {
                      const currentPage = parseInt(page);
                      if (currentPage <= 3) {
                        return i < 5;
                      }
                      if (currentPage >= totalPages - 2) {
                        return i >= totalPages - 5;
                      }
                      return i >= currentPage - 3 && i < currentPage + 2;
                    })
                    .map((i) => (
                      <PaginationItem key={i}>
                        <PaginationLink
                          href="#"
                          isActive={i + 1 === parseInt(page)}
                          onClick={() => updateParams({ page: i + 1 })}
                        >
                          {i + 1}
                        </PaginationLink>
                      </PaginationItem>
                    ))}
                  <PaginationItem>
                    <PaginationEllipsis />
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationNext
                      href="#"
                      onClick={() =>
                        updateParams({
                          page: Math.min(parseInt(page) + 1, totalPages),
                        })
                      }
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
            <div className="flex justify-center items-center mt-4">
              {/* pagesize */}
              {/* <select
                onChange={(e) =>
                  updateParams({ pageSize: +e.target.value, page: 1 })
                }
                value={pageSize}
                className="border border-gray-300 rounded-lg px-4 py-2 text-gray-800"
              >
                <option value="10">10 por página</option>
                <option value="20">20 por página</option>
                <option value="50">50 por página</option>
              </select> */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">{pageSize} por página</Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  {/* <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Billing</DropdownMenuItem>
                  <DropdownMenuItem>Team</DropdownMenuItem>
                  <DropdownMenuItem>Subscription</DropdownMenuItem> */}
                  <DropdownMenuItem
                    onSelect={() => updateParams({ pageSize: 10, page: 1 })}
                  >
                    10 por página
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={() => updateParams({ pageSize: 20, page: 1 })}
                  >
                    20 por página
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={() => updateParams({ pageSize: 50, page: 1 })}
                  >
                    50 por página
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
