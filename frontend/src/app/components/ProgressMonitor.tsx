"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { io, Socket } from "socket.io-client";

const SOCKET_SERVER_URL = "http://localhost:5001"; // URL do servidor backend

interface Log {
  type: string;
  message: string;
}

interface ScrapyProgressProps {
  isRunning: boolean;
  setIsRunning: (value: boolean) => void;
}

const ScrapyProgress = ({ isRunning, setIsRunning }: ScrapyProgressProps) => {
  const [logs, setLogs] = useState<Log[]>([]); // Lista de logs
  const scrollRef = useRef<HTMLDivElement>(null); // Referência para a caixa de rolagem
  const [isScrolled, setIsScrolled] = useState(false); // Controle de rolagem
  const router = useRouter();
  const MAX_VISIBLE_LOGS = 5; // Limite de mensagens visíveis

  useEffect(() => {
    const socket: Socket = io(SOCKET_SERVER_URL);

    socket.on("scrapy_progress", (data: { message: string }) => {
      setLogs((prevLogs) => {
        const newLogs = [
          ...prevLogs,
          { type: "progress", message: data.message },
        ];
        return newLogs.slice(-MAX_VISIBLE_LOGS); // Limita às últimas 5 mensagens
      });
      setIsRunning(true);
    });

    socket.on("scrapy_done", (data: { message: string }) => {
      setLogs((prevLogs) => [{ type: "done", message: data.message }]);
      setIsRunning(false);
      router.refresh(); // Recarrega a página para exibir os novos dados
    });

    socket.on("scrapy_error", (data: { message: string }) => {
      setLogs((prevLogs) =>
        [...prevLogs, { type: "error", message: data.message }].slice(
          -MAX_VISIBLE_LOGS
        )
      );
      setIsRunning(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!isScrolled && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isScrolled]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    setIsScrolled(scrollTop + clientHeight < scrollHeight - 5);
  };

  if (!isRunning && logs.length === 0) {
    return null; // Não exibe o componente se o Scrapy não estiver sendo executado
  }

  return (
    <div className="flex flex-col items-start justify-center w-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Progresso</h1>
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className={`w-full overflow-y-auto bg-gray-400 rounded-md shadow-md ${
          isRunning ? "h-40" : ""
        }`}
      >
        {logs.map((log, index) => {
          const isLastLog = index === logs.length - 1;
          const opacity = isScrolled ? 1 : 1 - (logs.length - index) * 0.2; // Opacidade decrescente
          return (
            <p
              key={index}
              className={`p-2 text-gray-800
                   ${isLastLog ? "bg-white font-bold" : "bg-gray-300"}`}
              style={{
                opacity: isLastLog ? 1 : Math.max(opacity, 0.2),
              }}
            >
              {log.message}
            </p>
          );
        })}
      </div>
    </div>
  );
};

export default ScrapyProgress;
