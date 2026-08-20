import { createServer } from 'vite'

export async function loadMacaronDetails(root) {
  const server = await createServer({
    root,
    configFile: false,
    logLevel: 'silent',
    server: { middlewareMode: true },
    appType: 'custom',
  })

  try {
    const module = await server.ssrLoadModule('/src/data/macaronDetails.ts')
    return module.macaronDetails
  } finally {
    await server.close()
  }
}
