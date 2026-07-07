let logoBase64: string | null = null

export async function getLogoBase64(): Promise<string> {
  if (logoBase64) return logoBase64
  const resp = await fetch('/img/logos/natus-logo.png')
  const blob = await resp.blob()
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => {
      logoBase64 = reader.result as string
      resolve(logoBase64)
    }
    reader.readAsDataURL(blob)
  })
}
