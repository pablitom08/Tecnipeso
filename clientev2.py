import socket
import sys
import CrearExcel
import time
import random

MAX_RETRIES = 30  # número máximo de intentos de conexión
INITIAL_BACKOFF = 5  # tiempo de espera inicial en segundos

class SensorStreamingTest(object):
    def __init__(self):
        self.sock = None
        self.connected = False
        self.cerrando = False
 
    def conectar(self, host, port, directorio):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, int(port))
        print('conectando a {} puerto {}'.format(*server_address))
        self.sock.connect(server_address)
        self.connected = True
        self.cerrando = False
        print('conexión establecida')

        while True:
            if not self.connected:
                print('perdida de conexión, intentando reconexión...')
                retry = 0
                while retry < MAX_RETRIES:
                    try:
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.sock.connect(server_address)
                        self.connected = True
                        print('conexión restablecida')
                        break
                    except socket.error as e:
                        print(f'no se pudo restablecer la conexión: {e}')
                        retry += 1
                        backoff = self.exponential_backoff(retry)
                        print(f'intentando de nuevo en {backoff} segundos...')
                        time.sleep(backoff)
                if not self.connected:
                    print('no se pudo restablecer la conexión después de varios intentos, deteniendo el cliente...')
                    break

            try:
                data = self.sock.recv(1024)
                if not data:
                    print('conexión cerrada por el servidor')
                    self.connected = False
                    continue
                datos=data.decode('UTF-8')
                CrearExcel.registro(datos,directorio)
                print(datos)
            except socket.error as e:
                print(f'error de socket: {e}')
                self.connected = False
                self.cerrando = False
                break

    def cerrar(self):
        self.cerrando = True
        self.connected = False
        try:
            if self.sock is not None:
                self.sock.close()
                print('socket cerrado')
            else:
                print('socket ya cerrado')
        except socket.error as e:
            print(f'error de socket al cerrar: {e}')


    def exponential_backoff(self, retry):
        backoff = INITIAL_BACKOFF * (2 ** retry) + random.randint(0, 1000)/1000
        return min(backoff, 600)  # límite de espera de 10 minutos


if __name__ == '__main__':
    h= '192.168.100.141'
    p=4001
    directorio=None
    SensorStreamingTest(h, p)
    MAX_RETRIES = 10  # número máximo de intentos de conexión
    INITIAL_BACKOFF = 5  # tiempo de espera inicial en segundos
