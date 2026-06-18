import DOMPurify from 'dompurify'

export function useSanitize() {
  function sanitizeHtml(html: string): string {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'blockquote', 'hr', 'a', 'img', 'sub', 'sup'],
      ALLOWED_ATTR: ['href', 'target', 'src', 'alt', 'title', 'class']
    })
  }

  return { sanitizeHtml }
}
