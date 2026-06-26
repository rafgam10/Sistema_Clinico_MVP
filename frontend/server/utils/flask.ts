/* eslint-disable @typescript-eslint/no-explicit-any */
import { getCookie } from 'h3'

export async function flaskFetch<T>(event: any, path: string, opts?: any): Promise<T> {
  const token = getCookie(event, 'auth_token')
  const config = useRuntimeConfig()

  return $fetch<T>(`${config.flaskBaseUrl}${path}`, {
    ...opts,
    headers: {
      ...opts?.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  }) as T
}
