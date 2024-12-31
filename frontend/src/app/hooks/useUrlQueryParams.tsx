"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect, useMemo } from "react";

interface UseUrlQueryParamsOptions {
  defaultParams?: Record<string, any>;
}

export function useUrlQueryParams(options: UseUrlQueryParamsOptions = {}) {
  const { defaultParams = {} } = options;
  const router = useRouter();

  const [params, setParams] = useState(() => {
    const currentUrl = new URL(window.location.href);
    const searchParams = new URLSearchParams(currentUrl.search);
    const initialParams: Record<string, any> = {};

    Object.keys(defaultParams).forEach((key) => {
      initialParams[key] = searchParams.get(key) || defaultParams[key];
    });

    return initialParams;
  });

  useEffect(() => {
    const currentUrl = new URL(window.location.href);
    const searchParams = new URLSearchParams(currentUrl.search);

    Object.keys(params).forEach((key) => {
      if (params[key] !== undefined) {
        searchParams.set(key, params[key]);
      }
    });

    currentUrl.search = searchParams.toString();
    router.push(currentUrl.toString());
  }, [params, router]);

  const updateParams = (updates: Record<string, any>) => {
    setParams((prevParams) => ({
      ...prevParams,
      ...updates,
    }));
  };

  const clearParams = () => {
    setParams(defaultParams);
  };

  return {
    params,
    updateParams,
    clearParams,
  };
}
