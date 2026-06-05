export default defineEventHandler(async (event) => {
  const { req, res } = event.node

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no'
  })

  // Send initial connection event
  res.write('event: connected\ndata: {}\n\n')

  // Keep alive
  const keepAlive = setInterval(() => {
    res.write(':keepalive\n\n')
  }, 15000)

  const remove = addSseClient({
    write: (data: string) => res.write(data),
    close: () => {
      clearInterval(keepAlive)
      res.end()
    }
  })

  req.on('close', () => {
    clearInterval(keepAlive)
    remove()
  })

  // Prevent nitro from ending the response
  return new Promise(() => {})
})
