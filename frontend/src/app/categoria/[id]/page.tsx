"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchConveniosByCategory } from "@/services/convenioService";
import Link from "next/link";
import { use } from "react";
import { useRouter } from "next/navigation";

interface CategoriaPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function CategoriaPage({ params }: CategoriaPageProps) {
  const { id } = use(params); // Acesso direto ao ID da categoria

  const {
    data: convenios,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["categoria", id],
    queryFn: () => fetchConveniosByCategory(id),
    enabled: !!id, // Apenas executa se o ID estiver disponível
  });
  const router = useRouter();

  if (isLoading) {
    return <p>Carregando convênios da categoria...</p>;
  }

  if (isError) {
    return <p>Erro ao carregar os convênios da categoria.</p>;
  }

  const decodedId = decodeURIComponent(id);

  return (
    <div className="container mx-auto py-10 px-6 rounded-lg shadow-lg">
      {/* Link para voltar */}
      <div className="mb-4">
        <Link href="#" onClick={router.back}>
          Voltar para a página inicial
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-blue-600">
        Convênios da categoria: {decodedId}
      </h1>

      {/* Lista de convênios */}
      <div className="space-y-4">
        {convenios.map((convenio: any) => (
          <div
            key={convenio.id}
            className="p-4 border border-gray-300 rounded-lg hover:shadow-md transition-shadow"
          >
            <h2 className="text-xl font-semibold text-blue-500">
              <Link href={`/convenios/${convenio.id}`}>{convenio.title}</Link>
            </h2>
            <p className="text-gray-500 text-sm mb-2">{convenio.date}</p>
            <p className="text-gray-700">{convenio.cats}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
