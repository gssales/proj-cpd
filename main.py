import pandas as pd
import struct
import copy

# =============================================
#   Funções úteis

# converte uma string utf-16 para um sequência de bytes
#  textos e títulos no youtube permitem caracteres especiais que só podem ser
#    representados por utf-16
def utf16_to_bytes(string):
    return bytes(string, 'utf-16')

# converte uma sequência de bytes para string utf-16
def bytes_to_utf16(byts):
    return byts.decode('utf-16')

# =============================================================================
# classe BTree
# usada para indexar strings exatas
#  indexa:
#    nome de canal
class BTree:

    def __init__(params):
        self.file_path = params['file_path']
        self.node_format = params['node_format']
        self.min_degree = params['min_degree']

    def search(self):
        print('a ser implementado')

    def insert(self):
        print('a ser implementado')

    def delete(self):
        print('a ser implementado')


# classe BTreeNode
# um nó de uma BTree
class BTreeNode:

    def __init__(params):
        self.nchaves = params['nchave']
        self.eh_folha = params['eh_folha']
        self.chaves = params['chaves']
        self.ponteiros = params['ponteiros']

    def search(self):
        print('a ser implementado')

    def insert(self):
        print('a ser implementado')

    def delete(self):
        print('a ser implementado')

# =============================================================================
# classe HashTableExt
class Bucket:

    def __init__(self, params):
        self.id_bloco = params['id_bloco']
        self.tam_bloco = 200
        self.qtd_videos = params['qtd_videos']
        self.local_depth = params['local_depth']
        self.videos = [None] * self.tam_bloco
        self.chaves = [None] * self.tam_bloco

    def busca_binaria_chave(self, chave):
        baixo = 0
        meio = 0
        alto = self.qtd_videos-1
        while baixo <= alto:
            meio = (baixo + alto) / 2
            if chave < self.chaves[meio]:
                alto = meio -1
            elif chave > self.chaves[meio]:
                baixo = meio +1
            return meio
        return meio

    def search(self, chave):
        meio = self.busca_binaria_chave(chave)
        return self.videos[meio]

    def insert(self, chave, valor):
        if self.isFull():
            return False
        
        meio = self.busca_binaria_chave(chave)

        for i in range(self.qtd_values, meio, -1):
            self.chaves[i] = self.chaves[i-1]
            self.videos[i] = self.videos[i-1]
            
        self.chaves[meio] = chave
        self.videos[meio] = valor
        self.qtd_videos += 1
        return True

    def delete(self, chave):
        meio = self.busca_binaria_chave(chave)
        
        for i in range(meio, self.qtd_videos):
            self.chaves[i] = self.chaves[i+1]
            self.videos[i] = self.videos[i+1]
        
        self.chaves[self.qtd_values -1] = None
        self.videos[self.qtd_videos -1] = None
        
        self.qtd_values -= 1

    def isFull(self):
        return self.qtd_videos == self.tam_bloco

    def isEmpty(self):
        return self.qtd_videos == 0

    def increaseDepth(self):
        self.local_depth += 1
        return self.local_depth
        
    def decreaseDepth(self):
        self.local_depth -= 1
        return self.local_depth
        
    def limpa(self):
        self.chaves = [None] * self.tam_bloco
        self.videos = [None] * self.tam_bloco
        
    def imprime(self):
        print('a ser implementado')

    def load(self):
        bloco_form = ('L'+Video.FORMAT)*self.tam_bloco
        try:
            with open(Video.FILE_PATH, 'rb') as f:
                f.seek(self.id_bloco * struct.calcsize(bloco_form))
                for i in range(0, self.qtd_videos):
                    pacote = f.read(struct.calcsize('L'))
                    self.chaves[i] = struct.unpack('L', pacote)[0]
                    pacote = f.read(struct.calcsize(Video.FORMAT))
                    self.videos[i] = Video.unpack(pacote)
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')
        
    def save(self):
        bloco_form = ('L'+Video.FORMAT)*self.tam_bloco
        with open(Video.FILE_PATH, 'ab') as f:
            f.seek(self.id_bloco * struct.calcsize(bloco_form))
            for i in range(0, self.qtd_videos):
                pacote = struct.pack('L', self.chaves[i])
                f.write(pacote)
                pacote = self.videos[i].pack()
                f.write(pacote)

# class Page
class Directory:

    FILE_PATH = 'dados/diretorio_video.bin'
    
    def __init__(self):
        self.global_depth = 1

        self.buckets = [] * (2**self.global_depth)
        self.buffer_bloco = None
        

    # método hash(chave): int
    #   dada uma chave de string, retorna uma valor inteiro como a pseudochave
    @staticmethod
    def hash(chave):
        pseudochave = 0
        for c in chave:
            pseudochave = ord(c) + 3*pseudochave
        return pseudochave

    @staticmethod
    def index(id_bucket, depth):
        return id_bucket ^ (1<<(depth-1))

    def calcula_bloco(self, chave):
        return chave & ((1<<self.global_depth)-1)

    # método crescer()
    #   aumenta a profundidade do diretório e reorganiza as entradas nos blocos
    def crescer(self):
        for i in range(0, 1<<self.global_depth):
            self.buckets.append(self.buckets[i])
        self.global_depth += 1

    # método encolher(): boolean
    #   diminui a profundidade do diretório
    # retorna True se deu certo
    # retorna False não é possível encolher o diretório
    def encolher(self):
        for bucket in self.buckets:
            if bucket.local_depth == self.global_depth:
                return False
        self.global_depth -= 1
        for i in range(0, 1<<self.global_depth):
            self.buckets.pop()
        return True

    # método dividir(id_bucket)
    #   dado um bucket lotado, tenta dividir o bucket em dois
    def dividir(self, id_bucket):
        local_depth = self.buckets[id_bucket].increaseDepth()
        if local_depth > self.global_depth:
            self.crescer()
        index_par = self.index(id_bucket, local_depth)
        self.buckets[index_par] = Bucket({
            'id_bloco': index_par,
            'local_depth': local_depth,
            'qtd_videos': 0 })
        temp = copy.deepcopy(self.buckets[id_bucket])
        temp.load()
        self.buckets[id_bucket].clear()
        index_diff = 1<<local_depth
        dir_size = 1<<self.global_depth
        for i in range(index_par-index_diff, 0, -index_diff):
            self.buckets[i] = self.buckets[index_par]
        for i in range(index_par+index_diff, dir_size, index_diff):
            self.buckets[i] = self.buckets[index_par]
        for video in temp.videos:
            self.insert(video.id, video);
        temp.limpa()

    def mergir(self, id_bucket):
        local_depth = self.buckets[id_bucket].local_depth
        index_par = self.index(id_bucket, local_depth)
        index_diff = 1<<local_depth
        dir_size = 1<<self.global_depth

        if self.buckets[index_par].local_depth == local_depth:
            self.bucket[index_par].decreaseDepth()
            for i in range(index_par-index_diff, 0, -index_diff):
                self.buckets[i] = self.buckets[index_par]
            for i in range(index_par+index_diff, dir_size, index_diff):
                self.buckets[i] = self.buckets[index_par]
        

    def search(self, id_string):
        chave = self.hash(id_string)
        id_bloco = self.calcula_bloco(chave)
        
        if self.buffer_bloco != None:
            if self.buffer_bloco.id_bloco != id_bloco:
                self.buffer_bloco.limpa()
                self.buffer_bloco = self.buckets[id_bloco]
                self.buffer_bloco.load()
        else:
            self.buffer_bloco = self.buckets[id_bloco]
            self.buffer_bloco.load()

        return self.buffer_bloco.search(chave)

    def insert(self, id_string, video):
        chave = self.hash(id_string)
        id_bloco = self.calcula_bloco(chave)
        
        if self.buffer_bloco != None:
            if self.buffer_bloco.id_bloco != id_bloco:
                self.buffer_bloco.limpa()
                self.buffer_bloco = self.buckets[id_bloco]
                self.buffer_bloco.load()
        else:
            self.buffer_bloco = self.buckets[id_bloco]
            self.buffer_bloco.load()
            
        result = self.buffer_bloco.insert(chave, video)
        if not result:
            self.dividir(id_bloco)
            self.insert(id_string, video)
        else:
            self.buffer_bloco.save()

    def delete(self, id_string):
        chave = self.hash(id_string)
        id_bloco = self.calcula_bloco(chave)

        if self.buffer_bloco != None:
            if self.buffer_bloco.id_bloco != id_bloco:
                self.buffer_bloco.limpa()
                self.buffer_bloco = self.buckets[id_bloco]
                self.buffer_bloco.load()
        else:
            self.buffer_bloco = self.buckets[id_bloco]
            self.buffer_bloco.load()

        self.buffer_bloco.delete(chave)
        if self.buffer_bloco.isEmpty() and self.buffer_bloco.local_depth > 1:
            self.mergir(id_bloco)
        self.encolher()

    def imprime(self):
        print('a ser implementado')

    def load(self):
        self.buckets = [] * 2**self.global_depth
        try:
            with open(Directory.FILE_PATH, 'rb') as f:
                pac = f.read(struct.calcsize('L'))
                self.global_depth = struct.unpack('L', pac)
                for i in range(0, 2^self.global_depth):
                    pac = f.read(struct.calcsize('LL'))
                    unpac = struct.unpack('LL', pac)
                    self.buckets.append(Bucket({
                        'id_bloco': i,
                        'local_depth': unpac[0],
                        'qtd_videos': unpac[1],
                        }))
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')
        
    def save(self):
        with open(Directory.FILE_PATH, 'wb') as f:
            pac = struct.pac('L', self.global_depth)
            f.write(pac)
            for i in range(0, 2^self.global_depth):
                pac = struct('LL',
                             self.buckets[i].local_depth,
                             self.buckets[i].qtd_videos)
                f.write(pac)

# =============================================================================
# classe Descritor
# Define uma classe de descritor (não pode ser instanciada)
#  Esta classe vai trabalhar com um arquivo auxiliar para armazenar informações
# sobre os outros arquivos, por exemplo, qtd de elementos, qtd de blocos
class Descritor:
    FILE_PATH = 'dados/descritor.bin'
    FORMAT = 'LL'

    def __init__(self):
        self.categoria_bin_size = 0
        self.canal_bin_size = 0

    # método load(): void
    # carrega as informações do arquivo descritor
    # deve ser chamado no inicio do aplicativo
    def load(self):
        try:
            with open(Descritor.FILE_PATH, 'rb') as f:
                buffer = f.read(struct.calcsize(Descritor.FORMAT))
                tupla = struct.unpack(Descritor.FORMAT, buffer)

                self.categoria_bin_size = tupla[0]
                self.canal_bin_size = tupla[1]
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')

    # método save(): void
    # guarda as informações no arquivo descritor
    # deve ser chamado ao terminar o aplicativo
    def save(self):
        with open(Descritor.FILE_PATH, 'wb') as f:
            pacote = struct.pack(Descritor.FORMAT,
                                 self.categoria_bin_size,
                                 self.canal_bin_size)
            f.write(pacote)    

# =============================================================================
# classe Categoria
# Define uma categoria
class Categoria:
    # (estático) (constante)
    FORMAT = '?L48s' # formato de um struct de Categoria
    # ? - boolean
    # L - unsigned long
    # 24s - string de 24 bytes (UTF-16)

    # (estático) (constante)
    FILE_PATH = 'dados/categorias.bin'

    # Categoria(params): Categoria
    # params é um dicionario com as seguintes entradas:
    #   ativo: bool - define se esta categoria é válida ou não
    #   id: int - o id da categoria no arquivo
    #       por questao de padrao de tipo de id, o id é um unsigned long, que
    #       permite bem mais categorias armazenadas no arquivos, mas o python
    #       não diferencia int de long, então não precisamos nos preocupar com
    #       isso aqui
    #   name: string -  o nome da categoria
    #         até 24 caracteres
    def __init__(self, params):
        self.ativo = params['ativo']
        self.id = params['id']
        self.nome = params['nome']

    # método imprime(): void
    #   imprime o id e o nome da categoria para fins de debug ou apresentação
    def imprime(self):
        print(str(self.ativo)+', id: '+str(self.id)+', categoria: '+self.nome)

    # método videos(): Video[]
    def videos(self):
        print('a ser implementado')

    # método save(): void
    #   salva o objeto categoria no arquivo, na posição correspondente ao id da
    #       categoria, preenche espaços vazios com false
    #   IMPORTANTE: Para o arquivo de categorias, usamos enderaçamento direto.
    #                com o id acessamos diretamente a categoria no arquivo com
    #                o deslocamento de bytes por conta disso o arquivo terá
    #                espaços vazios com lixo de memória
    def save(self):
        with open(Categoria.FILE_PATH, 'ab') as f:
            while self.id > descritor.categoria_bin_size:
                f.seek(descritor.categoria_bin_size *
                       struct.calcsize(Categoria.FORMAT))
                f.write(struct.pack(Categoria.FORMAT,
                                    False,
                                    0,
                                    utf16_to_bytes('$$$$$$$$$$$$$$$$$$$$$$$$')))
                descritor.categoria_bin_size += 1
            f.seek(self.id * struct.calcsize(Categoria.FORMAT))
            descritor.categoria_bin_size += 1
            f.write(self.pack())

    # método delete(): void
    #   deleta uma categoria no arquivo
    def delete(self):
        self.ativo = False
        if self.id < descritor.categoria_bin_size:
            with open(Categoria.FILE_PATH, 'ab') as f:
                f.seek(self.id * struct.calcsize(Categoria.FORMAT))
                f.write(struct.pack('?', False))

    # (estático) método get_by_id(id): Categoria
    #   busca um canal no arquivo de categorias pelo id, se o
    #     id nao existe retorna None
    def get_by_id(id_categoria):
        try:
            if id_categoria < descritor.categoria_bin_size:
                with open(Categoria.FILE_PATH, 'rb') as f:
                    f.seek(id_categoria * struct.calcsize(Categoria.FORMAT))
                    pacote = f.read(struct.calcsize(Categoria.FORMAT))
                    cat = Categoria.unpack(pacote)
                    if cat.ativo:
                        return cat
                    else:
                        return None
            else:
                return None
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')

    # método pack(): bytes
    #   'empacota' o objeto e codifica em uma sequência de bytes, que pode ser
    #     armazenada em um arquivo
    def pack(self):
        return struct.pack(Categoria.FORMAT,
                             self.ativo,
                             self.id,
                             utf16_to_bytes(self.nome))

    # (estático) método unpack(buffer): Categoria
    #   'desempacota' uma sequência de bytes e tenta reconstruir em objeto de
    #   categoria
    #   buffer: bytes - a sequência de bytes
    def unpack(buffer):
        # struct.unpack(...) retorna uma tupla com a sequencia em que o struct
        #   foi organizado nos bytes, no caso (bool, long, string)
        tupla = struct.unpack(Categoria.FORMAT, buffer)
        params = {
            'ativo': tupla[0],
            'id': tupla[1],
            'nome': bytes_to_utf16(tupla[2])
            }
        return Categoria(params)

# =============================================================================
# classe Canal
# Define um canal
class Canal:
    # (estático) (constante)
    FORMAT = '?L120s' # formato de um struct de Canal
    # ? - boolean
    # L - unsigned long
    # 60s - string de 60 bytes (UTF-16)

    # (estático) (constante)
    FILE_PATH = 'dados/canais.bin'

    # Canal(params): Canal
    # params é um dicionario com as seguintes entradas:
    #   ativo: boolean - se a entrada é ativa no arquivo
    #   id: int - o id da canal no arquivo
    #   name: string -  o nome do canal
    #         até 60 caracteres
    def __init__(self, params):
        self.ativo = params['ativo']
        self.id = params['id']
        self.nome = params['nome']

    # método save(): void
    #   se ja existe canal com este nome, atribui o id do canal existente no
    #    objeto senao, salva o objeto canal no fim arquivo, atribui o id como o
    #    tamanho do arquivo, e aumenta o tamanho do arquivo em +1
    #   IMPORTANTE: Para arquivos de canal, manteremos um arquivo que indexa o
    #                nome dos canais
    def save(self):
        # if existe no indice
            # atribui o id
        # else
        with open(Canal.FILE_PATH, 'ab') as f:
            self.id = descritor.canal_bin_size
            descritor.canal_bin_size += 1
            f.write(self.pack())

    # método delete(): void
    #   deleta um canal no arquivo
    def delete(self):
        self.ativo = False
        if self.id < descritor.canal_bin_size:
            with open(Canal.FILE_PATH, 'ab') as f:
                f.seek(self.id * struct.calcsize(Canal.FORMAT))
                f.write(struct.pack('?', False))

    # (estático) método get_by_id(id): Canal
    #   busca um canal no arquivo de canal pelo id
    def get_by_id(id_canal):
        try:
            if id_canal < descritor.canal_bin_size:
                with open(Canal.FILE_PATH, 'rb') as f:
                    f.seek(id_canal * struct.calcsize(Canal.FORMAT))
                    pacote = f.read(struct.calcsize(Canal.FORMAT))
                    canal = Canal.unpack(pacote)
                    if canal.ativo:
                        return canal
                    else:
                        return None
            else:
                return None
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')

    # método imprime(): void
    #   imprime o id e o nome do canal para fins de debug ou apresentação
    def imprime(self):
        print('id: '+self.id+', canal: '+self.nome)
        
    # método pack(): bytes
    #   'empacota' o objeto e codifica em uma sequência de bytes, que pode ser
    #     armazenada em um arquivo
    def pack(self):
        return struct.pack(Canal.FORMAT,
                             self.ativo,
                             self.id,
                             utf16_to_bytes(self.nome))

    # (estático) método unpack(buffer): Canal
    #   'desempacota' uma sequência de bytes e tenta reconstruir em objeto de
    #   canal
    #   buffer: bytes - a sequência de bytes
    def unpack(buffer):
        # struct.unpack(...) retorna uma tupla com a sequencia em que o struct
        #   foi organizado nos bytes, no caso (bool, long, string)
        tupla = struct.unpack(Canal.FORMAT, buffer)
        params = {
            'ativo': tupla[0],
            'id': tupla[1],
            'nome': bytes_to_utf16(tupla[2])
            }
        return Canal(params)
    
# =============================================================================
# classe Video
# Define um video
class Video:
    # (estático) (constante)
    FORMAT = '?22s200s510sLLL' # formato de um struct de VideoEmAlta
    # ?: boolean - se o vídeo é ativo no arquivo
    # 11s: string - a chave do vídeo
    # 100s: string - o título do vídeo
    # 255s: string - descrição
    # L: int - data e hora da publicação do vídeo
    # L: int - id da categoria
    # L: int - id do canal

    # (estático) (constante)
    FILE_PATH = 'dados/videos.bin'

    # Video(params): Video
    # params é um dicionario com as seguintes entradas:
    #   ativo: boolean - se o video é ativo no arquivo
    #   id: string - o id da video no arquivo
    #   title: string -  o título do vídeo
    #       até 100 chars
    #   description: string - a descrição do video
    #       até 255 chars
    #   publish_time: string - string da data e hora de publicação do vídeo
    #   id_categoria: int - o id da categoria do video
    #   id_canal: int - o id do canal do video
    def __init__(self, params):
        self.ativo = params['ativo']
        self.id = params['video_id']
        self.titulo = params['title']
        self.descricao = params['description']
        self.data_de_publicacao = params['publish_time']
        self.id_categoria = params['id_categoria']
        self.id_canal = params['id_canal']

        self.hashtable = Directory()
        self.hashtable.load()

    def categoria(self):
        return Categoria.get_by_id(self.id_categoria)

    def canal(self):
        return Canal.get_by_id(self.id_canal)

    # método save(): void
    #   se ja existe video com este id, o arquivo não é alterado
    #   senao o video é armazenado de acordo com o video de acordo coma
    #   hashtable
    #   IMPORTANTE: Para arquivo de video, usaremos uma hashtable extendivel
    #                para organizar os video.
    def save(self):
        self.hashtable.insert(self.id, self)

    # método delete(): void
    #   deleta um video no arquivo
    def delete(self):
        self.hashtable.remove(self.id)

    # (estático) método get_by_id(id): Video
    #   busca um Video no arquivo de video pelo id (chave da hashtable)
    def get_by_id(id_video):
        return self.hashtable(id_video)

    # método imprime(): void
    #   imprime o id e o nome do vídeo para fins de debug ou apresentação
    def imprime(self):
        print('Título do vídeo: '+self.titulo+'\nDescrição: '+self.descricao+'\nData: '+str(self.data_de_publicacao))
        
        canal = self.canal()
        if canal != None:
            canal.imprime()
        else:
            print('Nenhum canal')
            
        categoria = self.categoria()
        if categoria != None:
            categoria.imprime()
        else:
            print('Nenhma Categoria')
            
    # método pack(): bytes
    #   'empacota' o objeto e codifica em uma sequência de bytes, que pode ser
    #     armazenada em um arquivo
    def pack(self):
        return struct.pack(Video.FORMAT,
                           self.ativo,
                           utf16_to_bytes(self.id),
                           utf16_to_bytes(self.nome),
                           self.descricao,
                           self.data_de_publicacao,
                           self.id_categoria,
                           self.id_canal)

    # (estático) método unpack(buffer): Video
    #   'desempacota' uma sequência de bytes e tenta reconstruir em objeto de
    #   video
    #   buffer: bytes - a sequência de bytes
    def unpack(buffer):
        tupla = struct.unpack(Video.FORMAT, buffer)
        params = {
            'ativo': tupla[0],
            'id': bytes_to_utf16(tupla[1]),
            'title': bytes_to_utf16(tupla[2]),
            'description': tupla[3],
            'publish_time': tupla[4],
            'id_categoria': tupla[5],
            'id_canal': tupla[6]
            }
        return Video(params)

# =============================================================================
# classe VideoEmAlta
# Define um vídeo em alta
class VideoEmAlta:
    # (estático) (constante)
    FORMAT = '?11s4sIIII' # formato de um struct de VideoEmAlta
    # ?: boolean - se o vídeo é ativo no arquivo
    # 11s: string - a data em que o video estava em alta
    # 2c: chars - sigla do país em que o vídeo esteve em alta
    # I: int - qtd de views
    # I: int - qtd de likes
    # I: int - qtd de dislikes
    # I: int - qtd de comentarios

    # (estático) (constante)
    FILE_PATH = 'dados/trending.bin'

    # VideoEmAlta(params): VideoEmAlta
    # params é um dicionario com as seguintes entradas:
    #   ativo: boolean - se o video é ativo no arquivo
    #   id: string - o id da video no arquivo
    #   data: int - data em que o video estava em alta
    #   pais: string -  a sigla do pais em que o video esteve em alta
    #   views: int - qtd de views
    #   likes: int - qtd de likes
    #   dislikes: int - qtd de dislikes
    #   comments: int - qtd de comentarios
    def __init__(params):
        self.ativo = params['ativo']
        self.id_video = params['id_video']
        self.data = params['data']
        self.pais = params['pais']
        self.views = params['view_count']
        self.likes = params['likes']
        self.dislikes = params['dislikes']
        self.comments = params['comments']

    def video(self):
        return Video.get_by_id(self.id_video)

    # método save(): void
    #   se ja existe video em alta com este id nesta data, o arquivo não é
    #   alterado senao o video é armazenado de acordo com o objeto de acordo
    #   com a hashtable
    #   IMPORTANTE: Para arquivo de video, usaremos uma hashtable extendivel
    # 
    def save(self):
        print('a ser implementado')

    # (estático) método get_by_id(id): Video
    #   busca um Video no arquivo de video pelo id (chave da hashtable)
    def get_by_id(id_trend):
        print('a ser implementado')
        
    # método delete(): void
    #   deleta um video em alta no arquivo
    def delete(self):
        print('a ser implementado')

    # método pack(): bytes
    #   'empacota' o objeto e codifica em uma sequência de bytes, que pode ser
    #     armazenada em um arquivo
    def pack(self):
        return struct.pack(VideoEmAlta.FORMAT,
                           self.ativo,
                           self.id_video,
                           self.data,
                           self.pais,
                           self.views,
                           self.likes,
                           self.dislikes,
                           self.comments)

    # (estático) método unpack(buffer): VideoEmAlta
    #   'desempacota' uma sequência de bytes e tenta reconstruir em objeto de
    #   video em alta
    #   buffer: bytes - a sequência de bytes
    def unpack(buffer):
        tupla = struct.unpack(VideoEmAlta.FORMAT, buffer)
        params = {
            'ativo': tupla[0],
            'id_video': bytes_to_utf16(tupla[1]),
            'data': tupla[2],
            'pais': bytes_to_utf16(tupla[3]),
            'views': tupla[4],
            'likes': tupla[5],
            'dislikes': tupla[6],
            'comments': tupla[7]
            }
        return VideoEmAlta(params)

def busca_linear_id(array, id):
    for obj in array:
        if obj.id == id:
            return obj
    return None

def busca_linear_nome(array, nome):
    for obj in array:
        if obj.nome == nome:
            return obj
    return None

sair = False

descritor = Descritor()
descritor.load()

while(not sair):
    op = input('\nEscolha uma opção:'+
               '\n1. Inserir Vídeo'+
               '\n2. Listar Vídeos'+
               '\n3. Inserir Nova Categoria'+
               '\n4. Listar Categorias'+
               '\n5. Inserir Novo Canal'+
               '\n6. Listar Canais'+
               '\n7. Carregar arquivo de Videos em Alta'+
               '\n8. Carregar arquivo de categorias'+
               '\n9. Armazenar arquivo de categorias'+
               '\n10. Listar categorias do arquivo'+
               '\n11. Armazenar arquivo de canais'+
               '\n12. Listar canais de arquivo '+
               '\n99. Sair'+
               '\n\n> ')
    if op == '1':
        params = {
	    'title':'',
	    'description':'',
	    'publish_date':'', 
	    'categoria':None,
	    'canal':None
        }

        print('Escolha um canal:')
        for i,canal in enumerate(listaCanais):
            print(str(i)+'. ')
            canal.imprime()
        idxCanal = input('\n> ')
        params['canal'] = listaCanais[int(idxCanal)]

        params['title'] = input('\nInsira o nome do vídeo: ')
        params['description'] = input('\nDescrição: ')
        params['publish_date'] = input('\nData: ')
		
        print('Escolha uma categoria:')
        for i,cat in enumerate(listaCategoria):
            print(str(i)+'. ')
            cat.imprime()
        idxCat = input('\n> ')
        params['categoria'] = listaCategoria[int(idxCat)]

        listaVideos.append(Video(params))
		
    elif op == '2':
        for video in listaVideos:
            video.imprime()
            print('\n')
    elif op == '3':
        catname = input('\nInsira o nome da categoria: ')
        listaCategoria.append(Categoria({'name':catname}))

    elif op == '4':
        for categoria in listaCategoria:
            if categoria == None:
                print('None')
            else:
                categoria.imprime()

    elif op == '5':
        canalName = input('\nInsira o nome da canal: ')
        listaCanais.append(Canal({'name':canalName}))

    elif op == '6':
        for canal in listaCanais:
            canal.imprime()
            print('\n')

    elif op == '99':    
        descritor.save()
        sair = True

    elif op == '7':
        caminhoVideo = input('\nInsira o caminho do arquivo de videos: ')

        videos = pd.read_csv(caminhoVideo)
        for row in videos.itertuples():
            d = row._asdict()

            categoria = Categoria.get_by_id(int(d['category_id']))
            if categoria == None:
                categoria = Categoria.get_by_id(0)

            canal = Canal({
                'ativo': True,
                'id': 0,
                'nome':d['channel_title']})
            canal.save()

            d['ativo'] = True
            d['id_categoria'] = int(d['category_id'])
            d['id_canal'] = canal.id

            video = Video(d)
            video.save()

    elif op == '8':
        Categoria({'id':0, 'ativo':True, 'nome':'Nenhum'}).save()
        
        caminhoCategoria = input('Insira o caminho do arquivo de categoria: ')

        categorias = pd.read_json(caminhoCategoria)

        for item in categorias['items']:
            Categoria({
                    'id':int(item['id']),
                    'ativo':True,
                    'nome':item['snippet']['title']
                }).save()
            
    elif op == '9':
        Categoria.list_to_file(listaCategoria)

    elif op == '10':
        try:
            with open(Categoria.FILE_PATH, 'rb') as file:
                packet = file.read(struct.calcsize(Categoria.FORMAT))
                while packet:
                    cat = Categoria.unpack(packet)
                    if cat.ativo:
                        cat.imprime()
                    packet = file.read(struct.calcsize(Categoria.FORMAT))
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')

    elif op == '11':
        Canal.list_to_file(listaCanais)

    elif op == '12':
        try:
            with open('canais.bin', 'rb') as file:
                packet = file.read(struct.calcsize('48s'))
                while packet:
                    can = Canal.unpack(packet)
                    can.imprime()
                    packet = file.read(struct.calcsize('48s'))
        except FileNotFoundError:
            print('Nenhum arquivo encontrado')
