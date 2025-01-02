"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchConvenioById } from "@/services/convenioService";
import Link from "next/link";
import { useRouter } from "next/navigation";
import "./styles.css";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";

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
      <div className="mb-4">
        <Button onClick={router.back} variant={"outline"}>
          <ArrowLeft size={16} className="mr-2" />
          Voltar
        </Button>
      </div>
      <div className="flex space-x-2 items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-800 m-0">
          {convenio.title}
        </h1>
        <Badge>
          <a
            href={convenio.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1 cursor-pointer"
          >
            Ver no site <ExternalLink size={16} />
          </a>
        </Badge>
      </div>
      <p className="text-lg font-medium text-gray-700 mb-2">
        <span className="font-semibold">Data:</span>{" "}
        {new Date(convenio.date).toLocaleDateString()}
      </p>
      <p className="text-lg font-medium text-gray-700 mb-4">
        <span className="font-semibold">Categorias:</span>
      </p>
      {convenio.cats.split(", ").map((cat: string) => (
        <Badge
          key={cat}
          className="mr-2 cursor-pointer"
          variant={"outline"}
          onClick={() => router.push(`/categoria/${cat}`)}
        >
          {cat}
        </Badge>
      ))}
      <div className="mt-4">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Detalhes</h2>
        <div className="flex flex-col lg:flex-row gap-6">
          <div
            className="prose prose-lg max-w-none text-gray-800"
            dangerouslySetInnerHTML={{ __html: convenio.content }}
          />
        </div>
      </div>
    </div>
  );
}
