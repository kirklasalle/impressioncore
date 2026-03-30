import { useState, useCallback } from 'react';

interface ApiOptions {
    baseUrl?: string;
}

interface ApiResponse<T> {
    data: T | null;
    error: Error | null;
    isLoading: boolean;
}

export const useApi = (options: ApiOptions = {}) => {
    const baseUrl = options.baseUrl || '/api';

    const request = useCallback(
        async <T>(
            endpoint: string,
            method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
            data?: any
        ): Promise<ApiResponse<T>> => {
            const url = `${baseUrl}${endpoint}`;
            const headers = {
                'Content-Type': 'application/json',
            };

            try {
                const response = await fetch(url, {
                    method,
                    headers,
                    body: data ? JSON.stringify(data) : undefined,
                });

                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }

                // For DELETE requests that return no content
                if (method === 'DELETE' && response.status === 204) {
                    return { data: null, error: null, isLoading: false };
                }

                const responseData = await response.json();
                return { data: responseData, error: null, isLoading: false };
            } catch (error) {
                console.error('API request error:', error);
                return {
                    data: null,
                    error: error instanceof Error ? error : new Error(String(error)),
                    isLoading: false
                };
            }
        },
        [baseUrl]
    );

    return {
        get: <T>(endpoint: string) => request<T>(endpoint, 'GET'),
        post: <T>(endpoint: string, data: any) => request<T>(endpoint, 'POST', data),
        put: <T>(endpoint: string, data: any) => request<T>(endpoint, 'PUT', data),
        delete: <T>(endpoint: string) => request<T>(endpoint, 'DELETE'),
    };
};
