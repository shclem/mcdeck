import sys

from mc_args import MCArgs
from mc_progress import MCProgress
from mc_repo import MCRepo
from mc_pdf import MCPdf

def main() -> int:
    args = MCArgs()

    progress = MCProgress()

    repo = MCRepo(args, progress)

    pdf = MCPdf(args, progress)

    pdf.drawDecks(repo.buildDecks())

    pdf.output(args.output,'F').encode('latin-1')

    print('Success -> ' + args.output)

    return 0

if __name__ == '__main__':
    sys.exit(main())

