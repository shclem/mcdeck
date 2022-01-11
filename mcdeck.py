from mc_args import MCArgs
from mc_repo import MCRepo
from mc_pdf import MCPdf

args = MCArgs()

repo = MCRepo(args.language, args.deckIds)

pdf = MCPdf()

pdf.drawDecks(repo.buildDecks())

pdf.output(args.output,'F').encode('latin-1')
