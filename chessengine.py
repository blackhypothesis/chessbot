from subprocess import Popen, PIPE
from time import sleep
from chessbot.nbstreamreader import NonBlockingStreamReader as NBSR

# run the shell as a subprocess:
p = Popen(['/home/marcel/workspace/ChessAnalyse/assets/bin/stockfish'],
          stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False, universal_newlines=True)
# wrap p.stdout with a NonBlockingStreamReader object:
nbsr = NBSR(p.stdout)
# issue command:
# p.stdin.write(b'uci\n')
# p.stdin.flush()
# get the output

# for cmd in 'uci', 'd', 'position fen 1r6/1p3p1p/p4p2/1P6/8/5P2/2k3PP/5RK1 KQkq - 0 1', 'd', 'go':

for cmd in 'stop',\
        'setoption name Threads value 4',\
        'setoption name MultiPV value 3',\
        'position fen 1r6/1p3p1p/p4p2/1P6/8/5P2/2k3PP/5RK1 KQkq - 0 1',\
        'd',\
        'go depth 30',\
        :
    p.stdin.write(f'{cmd}\n')
    p.stdin.flush()

    line = 0
    while True:
        line += line
        output = nbsr.readline(0.1)
        # 0.1 secs to let the shell output the result
        if not output:
            print('### END of data ###')
            break
        print(f'{output}', end=',')

