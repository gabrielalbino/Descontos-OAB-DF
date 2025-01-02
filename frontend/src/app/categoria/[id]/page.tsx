"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchConveniosByCategory } from "@/services/convenioService";
import Link from "next/link";
import { use } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface CategoriaPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function CategoriaPage({ params }: CategoriaPageProps) {
  const { id } = use(params); // Acesso direto ao ID da categoria
  const decodedId = decodeURIComponent(id);

  const {
    data: convenios,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["categoria", id],
    queryFn: () => fetchConveniosByCategory(decodedId),
    enabled: !!id, // Apenas executa se o ID estiver disponível
  });
  const router = useRouter();

  if (isLoading) {
    return <p>Carregando convênios da categoria...</p>;
  }

  if (isError) {
    return <p>Erro ao carregar os convênios da categoria.</p>;
  }

  return (
    <div className="container mx-auto py-10 px-6 rounded-lg shadow-lg mt-6">
      {/* Link para voltar */}
      <div className="mb-4">
        <Button onClick={router.back}>
          <ArrowLeft size={16} className="mr-2" />
          Voltar
        </Button>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-blue-600">
        Convênios da categoria: {decodedId}
      </h1>

      {/* Lista de convênios */}
      <div className="space-y-4">
        {convenios?.data?.map((convenio: any) => (
          <Card
            className="w-full cursor-pointer"
            key={convenio.id}
            onClick={() => router.push(`/convenios/${convenio.id}`)}
          >
            <CardHeader className="flex items-center flex-row">
              <img
                src={convenio.image}
                alt={convenio.title}
                width={100}
                height={100}
                className="m-0"
              />
              <CardTitle>{convenio.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-2">
                {new Date(convenio.date).toLocaleDateString()}
                <Badge className="ml-2" variant={"outline"}>
                  {convenio.cats}
                </Badge>
              </CardDescription>
              {convenio.text}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
        
        
// <div
// key={convenio.id}
// className="p-4 border border-gray-300 rounded-lg hover:shadow-md transition-shadow"
// >
// <h2 className="text-xl font-semibold text-blue-500">
//   <Link href={`/convenios/${convenio.id}`}>{convenio.title}</Link>
// </h2>
// <div className="text-gray-500 text-sm mb-2 flex items-center gap-2">
//   <p>{new Date(convenio.date).toLocaleDateString()}</p>
//   <Badge className="ml-2" variant={"outline"}>
//     {convenio.cats}
//   </Badge>
// </div>
// <div className="text-gray-800">{convenio.text}</div>
// </div>
