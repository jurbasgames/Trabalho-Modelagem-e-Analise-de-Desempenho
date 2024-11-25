import datetime
import random
import matplotlib.pyplot as plt

TICK_RATE = 0.01  # 10ms duração do tick
WARM_UP = 10_000
N_JOBS = 10_000
SEED = 0

t_jobs = []  # Lista de tempo dos jobs no sistema após warmup
jobs_no_sistema = []


class Job:
    def __init__(self, id, t_inicio, estado="fila1", t_fim=None):
        self.id = id
        self.t_inicio = t_inicio
        self.t_fim = t_fim
        self.estado = estado
        self.skip: int = 0  # Tempo que o job tem que esperar no estado atual

    def saida(self, t_fim):
        self.t_fim = t_fim
        jobs_no_sistema.remove(self)
        delta = self.t_fim - self.t_inicio
        if self.id >= WARM_UP:
            t_jobs.append(delta)
            # print(f"{len(t_jobs)/(N_JOBS)*100:.2f}%")


class Servidor:
    def __init__(self, id, situacao, parametros):
        self.id = id
        self.job = None
        self.situacao = situacao
        self.parametros = parametros

    def tempo_servico(self):
        if self.situacao == 1:
            return self.parametros
        elif self.situacao == 2:
            return random.uniform(self.parametros[0], self.parametros[1])
        elif self.situacao == 3:
            return random.expovariate(1 / self.parametros)


class Fila:
    def __init__(self):
        self.jobs = []

    def add(self, job):
        self.jobs.append(job)

    def pop(self):
        return self.jobs.pop(0)


def event_loop(tempos_de_chegada, Fila1, Fila2, Fila3, Servidor1, Servidor2, Servidor3, tempo=0):
    job_id = 0
    cont = 0

    tempos = []
    fila1_tam = []
    fila2_tam = []
    fila3_tam = []
    servidor1_status = []
    servidor2_status = []
    servidor3_status = []

    while len(tempos_de_chegada) or len(jobs_no_sistema):
        if len(tempos_de_chegada) and tempos_de_chegada[0] <= tempo:
            while len(tempos_de_chegada) and tempos_de_chegada[0] <= tempo:
                tempos_de_chegada.pop(0)
                job = Job(job_id, tempo)
                job_id += 1
                jobs_no_sistema.append(job)
                Fila1.add(job)

        for job in jobs_no_sistema[:]:
            if job.skip > 0:
                job.skip -= TICK_RATE
                continue
            elif job.estado == "fila1":
                if Servidor1.job == None and Fila1.jobs[0] == job:
                    Servidor1.job = job
                    job.estado = "servidor1"
                    job.skip = Servidor1.tempo_servico()
                    Fila1.pop()
                else:
                    continue
            elif job.estado == "servidor1":
                if random.random() < 0.5:
                    Fila2.add(job)
                    job.estado = "fila2"
                else:
                    Fila3.add(job)
                    job.estado = "fila3"
                Servidor1.job = None

            elif job.estado == "fila2":
                if Servidor2.job == None and Fila2.jobs[0] == job:
                    Servidor2.job = job
                    job.estado = "servidor2"
                    job.skip = Servidor2.tempo_servico()
                    Fila2.pop()
                else:
                    continue

            elif job.estado == "servidor2":
                if random.random() < 0.2:
                    Fila2.add(job)
                    job.estado = "fila2"
                else:
                    job.saida(tempo)
                Servidor2.job = None

            elif job.estado == "fila3":
                if Servidor3.job == None and Fila3.jobs[0] == job:
                    Servidor3.job = job
                    job.estado = "servidor3"
                    job.skip = Servidor3.tempo_servico()
                    Fila3.pop()
                else:
                    continue

            elif job.estado == "servidor3":
                job.saida(tempo)
                Servidor3.job = None

        cont += 1
        if cont % 100 == 0:
            tempos.append(tempo)
            fila1_tam.append(len(Fila1.jobs))
            fila2_tam.append(len(Fila2.jobs))
            fila3_tam.append(len(Fila3.jobs))
            servidor1_status.append(1 if Servidor1.job else 0)
            servidor2_status.append(1 if Servidor2.job else 0)
            servidor3_status.append(1 if Servidor3.job else 0)

        tempo += TICK_RATE

    return tempos, fila1_tam, fila2_tam, fila3_tam, servidor1_status, servidor2_status, servidor3_status


def calcular_tempos_de_chegada():
    tempos_de_chegada = []
    t = 0
    total_jobs = WARM_UP + N_JOBS
    for _ in range(total_jobs):
        t += random.expovariate(2)
        tempos_de_chegada.append(t)
    return tempos_de_chegada


def main():

    random.seed()
    for situacao in [1, 2, 3]:
        print(
            f"------------------------------------------------------------------------------")
        print(f"Iniciando simulação para a Situação {situacao}...")
        tempos_de_chegada = calcular_tempos_de_chegada()

        Fila1 = Fila()
        Fila2 = Fila()
        Fila3 = Fila()

        if situacao == 1:
            Servidor1 = Servidor(1, 1, 0.4)
            Servidor2 = Servidor(2, 1, 0.6)
            Servidor3 = Servidor(3, 1, 0.95)
        elif situacao == 2:
            Servidor1 = Servidor(1, 2, (0.1, 0.7))
            Servidor2 = Servidor(2, 2, (0.1, 1.1))
            Servidor3 = Servidor(3, 2, (0.1, 1.8))
        elif situacao == 3:
            Servidor1 = Servidor(1, 3, 0.4)
            Servidor2 = Servidor(2, 3, 0.6)
            Servidor3 = Servidor(3, 3, 0.95)

        tempos, fila1_tam, fila2_tam, fila3_tam, servidor1_status, servidor2_status, servidor3_status = event_loop(tempos_de_chegada, Fila1, Fila2, Fila3,
                                                                                                                   Servidor1, Servidor2, Servidor3)

        tempo_medio = sum(t_jobs) / len(t_jobs)
        variancia = sum([(x - tempo_medio) ** 2 for x in t_jobs]
                        ) / (len(t_jobs))
        desvio_padrao = variancia ** 0.5

        print(
            f"-----------------------------------Situação-{situacao}---------------------------------")
        print(f"Tempo médio no sistema: {tempo_medio:.4f}s")
        print(f"Desvio padrão: {desvio_padrao:.4f}s")

        # Tempos dos jobs no sistema
        plt.figure(figsize=(10, 6))
        plt.hist(t_jobs, bins=50, density=False, color='blue')
        plt.title(f"Duração dos jobs no sistema - Situação {situacao}")
        plt.xlabel("Tempo (segundos)")
        plt.ylabel("Jobs")
        plt.grid(True)
        plt.savefig(f"graficos/histograma_situacao_{situacao}.png")
        plt.close('all')

        # Tamanho das filas
        plt.figure(figsize=(10, 6))
        plt.plot(tempos, fila1_tam, label='Fila 1')
        plt.plot(tempos, fila2_tam, label='Fila 2')
        plt.plot(tempos, fila3_tam, label='Fila 3')
        plt.title(f"Tamanho das filas - Situação {situacao}")
        plt.xlabel("Tempo (segundos)")
        plt.ylabel("Tamanho da fila")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"graficos/tamanho_filas_situacao_{situacao}.png")
        plt.close('all')

        # Utilização
        utilizacao_servidor1 = sum(servidor1_status) / len(servidor1_status)
        utilizacao_servidor2 = sum(servidor2_status) / len(servidor2_status)
        utilizacao_servidor3 = sum(servidor3_status) / len(servidor3_status)

        plt.figure(figsize=(8, 6))
        servidores = ['Servidor 1', 'Servidor 2', 'Servidor 3']
        utilizacoes = [utilizacao_servidor1*100,
                       utilizacao_servidor2*100, utilizacao_servidor3*100]
        plt.bar(servidores, utilizacoes, color=['blue', 'red', 'green'])
        plt.title(f"Utilização média - Situação {situacao}")
        plt.ylabel("Utilização (%)")
        plt.ylim(0, 100)
        plt.grid(axis='y')
        plt.savefig(
            f"graficos/utilizacao_media_servidores_situacao_{situacao}.png")
        plt.close('all')

        jobs_no_sistema.clear()
        t_jobs.clear()


if __name__ == "__main__":
    main()
