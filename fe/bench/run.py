from fe.bench.workload import Workload
from fe.bench.session import Session


def run_bench():
    wl = Workload()
    wl.gen_database()

    sessions = []
    for i in range(0, wl.session):
        ss = Session(wl)
        sessions.append(ss)

    for ss in sessions:
        ss.start()

    for ss in sessions:
        ss.join()


#if __name__ == "__main__":
#    run_bench()