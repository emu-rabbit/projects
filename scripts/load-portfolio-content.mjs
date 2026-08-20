import { createServer } from 'vite'

export async function loadPortfolioContent(root) {
  const server = await createServer({
    root,
    configFile: false,
    logLevel: 'silent',
    server: { middlewareMode: true },
    appType: 'custom',
  })

  try {
    const [detailModule, portfolioModule] = await Promise.all([
      server.ssrLoadModule('/src/data/macaronDetails.ts'),
      server.ssrLoadModule('/src/data/portfolio.ts'),
    ])
    return {
      macaronDetails: detailModule.macaronDetails,
      portfolioCopy: portfolioModule.portfolioCopy,
    }
  } finally {
    await server.close()
  }
}
