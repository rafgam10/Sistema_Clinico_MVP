type SseHandler = (data: unknown) => void

let eventSource: EventSource | null = null
const handlers = new Map<string, Set<SseHandler>>()
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

function handleEvent(eventType: string, raw: string) {
  try {
    const data = JSON.parse(raw)
    handlers.get(eventType)?.forEach(h => h(data))
  } catch { /* ignore malformed */ }
}

function connectShared() {
  if (eventSource && eventSource.readyState !== EventSource.CLOSED) return

  eventSource = new EventSource('/api/sse')

  eventSource.onerror = () => {
    eventSource?.close()
    reconnectTimer = setTimeout(connectShared, 3000)
  }

  eventSource.addEventListener('paciente:status', (e) => {
    handleEvent('paciente:status', e.data)
  })
  eventSource.addEventListener('chamado:novo', (e) => {
    handleEvent('chamado:novo', e.data)
  })
  eventSource.addEventListener('chamado:concluido', (e) => {
    handleEvent('chamado:concluido', e.data)
  })
}

export function useSse() {
  function on(event: string, handler: SseHandler) {
    if (!handlers.has(event)) {
      handlers.set(event, new Set())
    }
    handlers.get(event)!.add(handler)
    connectShared()
  }

  function off(event: string, handler: SseHandler) {
    handlers.get(event)?.delete(handler)
  }

  function connect() {
    connectShared()
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  return { on, off, connect, disconnect }
}
