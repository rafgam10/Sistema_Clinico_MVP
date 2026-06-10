const elapsed = ref(0)
const isRunning = ref(false)

let startTimestamp: number | null = null
let interval: ReturnType<typeof setInterval> | null = null

function start() {
  if (isRunning.value) return
  startTimestamp = Date.now() - elapsed.value * 1000
  isRunning.value = true
  interval = setInterval(() => {
    if (startTimestamp) {
      elapsed.value = Math.floor((Date.now() - startTimestamp) / 1000)
    }
  }, 1000)
}

function pause() {
  if (!isRunning.value) return
  if (interval) clearInterval(interval)
  interval = null
  if (startTimestamp) {
    elapsed.value = Math.floor((Date.now() - startTimestamp) / 1000)
  }
  isRunning.value = false
}

function resume() {
  start()
}

function stop(): number {
  if (interval) clearInterval(interval)
  interval = null
  if (startTimestamp) {
    elapsed.value = Math.floor((Date.now() - startTimestamp) / 1000)
  }
  isRunning.value = false
  startTimestamp = null
  const total = elapsed.value
  elapsed.value = 0
  return total
}

const formatted = computed(() => {
  const h = Math.floor(elapsed.value / 3600)
  const m = Math.floor((elapsed.value % 3600) / 60)
  const s = elapsed.value % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

export function useCronometro() {
  return { elapsed, isRunning, formatted, start, pause, resume, stop }
}
