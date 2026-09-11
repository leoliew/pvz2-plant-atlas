/**
 * Resolve a file from Vite's public directory while preserving the deployment
 * base path. GitHub project Pages live at /<repository>/ rather than /.
 */
export function assetUrl(path) {
  const relativePath = String(path).replace(/^\/+/, '');
  return `${import.meta.env.BASE_URL}${relativePath}`;
}
