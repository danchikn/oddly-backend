import uvloop

from src.worker import start_worker

if __name__ == '__main__':
    uvloop.run(start_worker())
