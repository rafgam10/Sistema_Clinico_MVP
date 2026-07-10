const sseClients: Set<{ write: (data: string) => void, close: () => void }> = new Set()

export function addSseClient(client: { write: (data: string) => void, close: () => void }) {
  sseClients.add(client)
  return () => {
    sseClients.delete(client)
  }
}

export function broadcastSse(event: { type: string, data: unknown }) {
  const message = `event: ${event.type}\ndata: ${JSON.stringify(event.data)}\n\n`
  for (const client of [...sseClients]) {
    try {
      client.write(message)
    } catch {
      sseClients.delete(client)
    }
  }
}
