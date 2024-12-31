"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchConvenioById } from "@/services/convenioService";
import Link from "next/link";
import { useRouter } from "next/navigation";
import "./styles.css";

interface ConvenioPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ConvenioPage({ params }: ConvenioPageProps) {
  const { id } = use(params); // Resolve a Promise de params para obter o ID

  const {
    data: convenio,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["convenio", id],
    queryFn: () => fetchConvenioById(id),
    enabled: !!id, // Apenas executa se o ID estiver disponível
  });
  const router = useRouter();

  if (isLoading) {
    return <p>Carregando detalhes do convênio...</p>;
  }

  if (isError) {
    return <p>Erro ao carregar os detalhes do convênio.</p>;
  }

  return (
    <div className="container mx-auto py-10 px-6 rounded-lg shadow-lg">
      {/* voltar  */}
      <div className="mb-4">
        <Link href="#" onClick={router.back}>
          Voltar
        </Link>
      </div>
      <h1 className="text-3xl font-bold mb-6 text-blue-600">
        {convenio.title}
      </h1>
      <p className="text-lg font-medium text-gray-300 mb-2">
        <span className="font-semibold">Data:</span> {convenio.date}
      </p>
      <p className="text-lg font-medium text-gray-300 mb-4">
        <span className="font-semibold">Categorias:</span> {convenio.cats}
      </p>
      <div className="mt-4">
        <h2 className="text-2xl font-semibold text-white-200 mb-4">Detalhes</h2>
        <div className="flex flex-col lg:flex-row gap-6">
          <div
            className="prose prose-lg max-w-none text-gray-200"
            dangerouslySetInnerHTML={{ __html: convenio.content }}
          />
        </div>
      </div>
    </div>
  );
}
