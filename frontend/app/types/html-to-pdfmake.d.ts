declare module 'html-to-pdfmake' {
  type PdfMakeContent = Record<string, unknown>
  const htmlToPdfmake: (html: string, options?: { window?: Window }) => PdfMakeContent[]
  export default htmlToPdfmake
}
