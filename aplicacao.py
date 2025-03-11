import sys
from PyQt5 import QtWidgets, uic
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Integer, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String


#Conexão com o banco de dados
engine = create_engine("sqlite:///data_bank.db", echo=True)
Session = sessionmaker(bind=engine)

#Criação das tabelas
class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "Usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(15), nullable=False)  # Ex: admin, professor, aluno

class Aluno(Base):
    __tablename__ = "Alunos"
    id: Mapped[int]                 = mapped_column(Integer, primary_key=True, autoincrement=True)
    fullname: Mapped[str]           = mapped_column(String(30), nullable=False)
    datanascimento: Mapped[Date]    = mapped_column(Date)
    cpf: Mapped[str]                = mapped_column(String, unique=True, nullable=False)

class Professor(Base):
    __tablename__ = "Professores"
    id: Mapped[int]                 = mapped_column(Integer, primary_key=True, autoincrement=True)
    fullname: Mapped[str]           = mapped_column(String(30), nullable=False)
    curso: Mapped[int]              = mapped_column(Integer, ForeignKey("Cursos.id"), nullable=False)
    datanascimento: Mapped[Date]    = mapped_column(Date)
    cpf: Mapped[str]                = mapped_column(String, unique=True, nullable=False)

    curso_rel: Mapped["Curso"] = relationship("Curso", back_populates="professores")

class Curso(Base):
    __tablename__ = "Cursos"
    id: Mapped[int]         = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]       = mapped_column(String(30), nullable=False)

    professores: Mapped[list["Professor"]] = relationship("Professor", back_populates="curso_rel")

#Cria as tabelas no BD
Base.metadata.create_all(engine)

#Cria a interface de python que contem as alterações feitas com CRUD
class CrudApp(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()



    def init_ui(self):
        #abas do Aluno, Professor e Curso
        self.tab_aluno = QtWidgets.QWidget()
        self.tab_professor = QtWidgets.QWidget()
        self.tab_curso = QtWidgets.QWidget()

        self.addTab(self.tab_aluno, "Aluno")
        self.addTab(self.tab_professor, "Professor")
        self.addTab(self.tab_curso, "Curso")

        #Chama as funções que criam as interfaces das abas
        self.init_aluno_tab()
        self.init_professor_tab()
        self.init_curso_tab()

        self.setWindowTitle("CRUD Aluno, Professor e Curso")
        #definindo o tamanho inicial da janela e posição
        self.setGeometry(100, 100, 600, 400)

        self.tab_usuario = QtWidgets.QWidget()
        self.addTab(self.tab_usuario, "Usuário")
        self.init_usuario_tab()

        self.btn_start_transaction = QtWidgets.QPushButton("Iniciar Transação")
        self.btn_commit_transaction = QtWidgets.QPushButton("Confirmar Transação")
        self.btn_rollback_transaction = QtWidgets.QPushButton("Desfazer Transação")


    #funções para criar as abas da interface
    def init_aluno_tab(self):
        layout = QtWidgets.QVBoxLayout() #usado para empilhar os widgets de froma vertical dentro da tabela

        #Inputs de Aluno
        self.input_nome_aluno = QtWidgets.QLineEdit()
        self.input_nome_aluno.setPlaceholderText("Nome do Aluno")
        self.input_birth_aluno = QtWidgets.QLineEdit()
        self.input_birth_aluno.setPlaceholderText("Data de Nascimento (dd-mm-yyyy)")
        self.input_cpf_aluno = QtWidgets.QLineEdit()
        self.input_cpf_aluno.setPlaceholderText("CPF")

        #Botões CRUD para Aluno
        self.btn_create_aluno = QtWidgets.QPushButton("Criar Aluno")
        self.btn_read_aluno = QtWidgets.QPushButton("Ler Alunos")
        self.btn_update_aluno = QtWidgets.QPushButton("Atualizar Aluno")
        self.btn_delete_aluno = QtWidgets.QPushButton("Deletar Aluno")

        #Tabela para exibir os Alunos
        self.table_aluno = QtWidgets.QTableWidget()
        self.table_aluno.setColumnCount(3)
        self.table_aluno.setHorizontalHeaderLabels(["Nome", "Nascimento", "CPF"])

        #Layout de inputs e botões
        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Nome:", self.input_nome_aluno)
        input_layout.addRow("Nascimento:", self.input_birth_aluno)
        input_layout.addRow("CPF:", self.input_cpf_aluno)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_create_aluno)
        button_layout.addWidget(self.btn_read_aluno)
        button_layout.addWidget(self.btn_update_aluno)
        button_layout.addWidget(self.btn_delete_aluno)

        # Monta o layout da aba Aluno
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_aluno)
        self.tab_aluno.setLayout(layout)

        #Conectar botões às funções CRUD de Aluno
        self.btn_create_aluno.clicked.connect(self.create_aluno)
        self.btn_read_aluno.clicked.connect(self.read_aluno)
        self.btn_update_aluno.clicked.connect(self.update_aluno)
        self.btn_delete_aluno.clicked.connect(self.delete_aluno)

    def create_aluno(self):
        session = Session()
        nome = self.input_nome_aluno.text()
        nascimento = self.input_birth_aluno.text()
        cpf = self.input_cpf_aluno.text()

        try:
            aluno = Aluno(  fullname=nome, 
                            datanascimento=datetime.strptime(nascimento, "%d-%m-%Y").date(), 
                            cpf=cpf)
            session.add(aluno)
            session.commit()
            self.read_aluno()  #Atualiza a tabela
            self.clear_inputs(self.input_nome_aluno, self.input_birth_aluno, self.input_cpf_aluno)
        except Exception as e:
            print(f"Erro ao criar aluno: {e}")
            session.rollback()
        finally:
            session.close()

    def read_aluno(self):
        session = Session()
        alunos = session.query(Aluno).all()
        self.table_aluno.setRowCount(0)  #Limpa a tabela antes de preencher
        for aluno in alunos:
            row_position = self.table_aluno.rowCount()
            self.table_aluno.insertRow(row_position)
            self.table_aluno.setItem(row_position, 0, QtWidgets.QTableWidgetItem(aluno.fullname))
            self.table_aluno.setItem(row_position, 1, QtWidgets.QTableWidgetItem(aluno.datanascimento.strftime('%d-%m-%Y')))
            self.table_aluno.setItem(row_position, 2, QtWidgets.QTableWidgetItem(aluno.cpf))
        session.close()

    def update_aluno(self):
        session = Session()
        aluno_id = self.table_aluno.currentRow() + 1  # fazendo o ID baseado na linha
        nome = self.input_nome_aluno.text()
        nascimento = self.input_birth_aluno.text()
        cpf = self.input_cpf_aluno.text()
        aluno = session.query(Aluno).filter_by(id=aluno_id).first()
        if aluno:
            try:
                aluno.fullname = nome
                aluno.datanascimento = datetime.strptime(nascimento, "%d-%m-%Y").date()
                aluno.cpf = cpf
                session.commit()
                self.read_aluno()  #Atualiza a tabela
            except Exception as e:
                print(f"Erro ao atualizar aluno: {e}")
                session.rollback()
        session.close()

    def delete_aluno(self):
        session = Session()
        aluno_id = self.table_aluno.currentRow() + 1  #ID baseado na linha
        aluno = session.query(Aluno).filter_by(id=aluno_id).first()
        if aluno:
            try:
                session.delete(aluno)
                session.commit()
                self.read_aluno()  #Atualiza a tabela
            except Exception as e:
                print(f"Erro ao deletar aluno: {e}")
                session.rollback()
        session.close()

    def init_usuario_tab(self):
        layout = QtWidgets.QVBoxLayout()

        # Inputs de Usuário
        self.input_username = QtWidgets.QLineEdit()
        self.input_username.setPlaceholderText("Nome de Usuário")
        self.input_password = QtWidgets.QLineEdit()
        self.input_password.setPlaceholderText("Senha")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_role = QtWidgets.QComboBox()
        self.input_role.addItems(["admin", "professor", "aluno"])

        # Botões CRUD para Usuário
        self.btn_create_user = QtWidgets.QPushButton("Criar Usuário")
        self.btn_read_user = QtWidgets.QPushButton("Ler Usuários")
        self.btn_update_user = QtWidgets.QPushButton("Atualizar Usuário")
        self.btn_delete_user = QtWidgets.QPushButton("Deletar Usuário")

        # Tabela para exibir os Usuários
        self.table_usuario = QtWidgets.QTableWidget()
        self.table_usuario.setColumnCount(3)
        self.table_usuario.setHorizontalHeaderLabels(["Nome de Usuário", "Senha", "Role"])

        # QLabel para exibir resultados
        self.result_label = QtWidgets.QLabel()  # Aqui é onde vamos mostrar os resultados
        self.result_label.setWordWrap(True)  # Permite quebra de linha no texto

        # Layout de inputs e botões
        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Usuário:", self.input_username)
        input_layout.addRow("Senha:", self.input_password)
        input_layout.addRow("Role:", self.input_role)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_create_user)
        button_layout.addWidget(self.btn_read_user)
        button_layout.addWidget(self.btn_update_user)
        button_layout.addWidget(self.btn_delete_user)

        # Monta o layout da aba Usuário
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_usuario)
        layout.addWidget(self.result_label)  # Adiciona o QLabel para mostrar o resultado
        self.tab_usuario.setLayout(layout)

        # Conectar botões às funções CRUD
        self.btn_create_user.clicked.connect(self.create_usuario)
        self.btn_read_user.clicked.connect(self.read_usuario)
        self.btn_update_user.clicked.connect(self.update_usuario)
        self.btn_delete_user.clicked.connect(self.delete_usuario)


    #funções para Professor
    def init_professor_tab(self):
        layout = QtWidgets.QVBoxLayout()  #usado para empilhar os widgets de froma vertical dentro da tabela

        #Inputs de Professor
        self.input_nome_professor = QtWidgets.QLineEdit()
        self.input_nome_professor.setPlaceholderText("Nome do Professor")
        self.input_birth_professor = QtWidgets.QLineEdit()
        self.input_birth_professor.setPlaceholderText("Data de Nascimento (dd-mm-yyyy)")
        self.input_cpf_professor = QtWidgets.QLineEdit()
        self.input_cpf_professor.setPlaceholderText("CPF")
        self.input_curso_professor = QtWidgets.QComboBox()
        self.update_curso_combobox()

        
        #Botões CRUD para Professor
        self.btn_create_professor = QtWidgets.QPushButton("Criar Professor")
        self.btn_read_professor = QtWidgets.QPushButton("Ler Professores")
        self.btn_update_professor = QtWidgets.QPushButton("Atualizar Professor")
        self.btn_delete_professor = QtWidgets.QPushButton("Deletar Professor")

        #tabela para exibir os Professores
        self.table_professor = QtWidgets.QTableWidget()
        self.table_professor.setColumnCount(4)
        self.table_professor.setHorizontalHeaderLabels(["Nome", "Nascimento", "CPF", "Curso"])

        #layout de inputs e botões
        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Nome:", self.input_nome_professor)
        input_layout.addRow("Nascimento:", self.input_birth_professor)
        input_layout.addRow("CPF:", self.input_cpf_professor)
        input_layout.addRow("Curso:", self.input_curso_professor)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_create_professor)
        button_layout.addWidget(self.btn_read_professor)
        button_layout.addWidget(self.btn_update_professor)
        button_layout.addWidget(self.btn_delete_professor)

        #monta o layout da aba Professor
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_professor)
        self.tab_professor.setLayout(layout)
        
        #Conectar botões às funções CRUD de Professor
        self.btn_create_professor.clicked.connect(self.create_professor)
        self.btn_read_professor.clicked.connect(self.read_professor)
        self.btn_update_professor.clicked.connect(self.update_professor)
        self.btn_delete_professor.clicked.connect(self.delete_professor)

    def update_curso_combobox(self):
        session = Session()
        cursos = session.query(Curso).all()
        self.input_curso_professor.clear()  # Limpa o combobox antes de recarregar
        for curso in cursos:
            self.input_curso_professor.addItem(curso.name, curso.id)  # Exibe o nome, mas armazena o ID
        session.close()

    def create_professor(self):
        session = Session()
        nome = self.input_nome_professor.text()
        nascimento = self.input_birth_professor.text()
        cpf = self.input_cpf_professor.text()
        curso_id = self.input_curso_professor.currentData()  #Obtem o ID do curso selecionado


        try:
            professor = Professor(  fullname=nome, 
                                    datanascimento=datetime.strptime(nascimento, "%d-%m-%Y").date(), 
                                    cpf=cpf, 
                                    curso=curso_id)
            session.add(professor)
            session.commit()
            self.read_professor()  #atualiza a tabela
            self.clear_inputs(self.input_nome_professor, self.input_birth_professor, self.input_cpf_professor, self.input_curso_professor)
        except Exception as e:
            print(f"Erro ao criar professor: {e}")
            session.rollback()
        finally:
            session.close()

    def read_professor(self):
        session = Session()
        professores = session.query(Professor).all()
        self.table_professor.setRowCount(0)  #Limpa a tabela antes de preencher
        for professor in professores:
            row_position = self.table_professor.rowCount()
            self.table_professor.insertRow(row_position)
            self.table_professor.setItem(row_position, 0, QtWidgets.QTableWidgetItem(professor.fullname))
            self.table_professor.setItem(row_position, 1, QtWidgets.QTableWidgetItem(professor.datanascimento.strftime('%d-%m-%Y')))
            self.table_professor.setItem(row_position, 2, QtWidgets.QTableWidgetItem(professor.cpf))
            self.table_professor.setItem(row_position, 3, QtWidgets.QTableWidgetItem(professor.curso_rel.name))
        session.close()

    def update_professor(self):
        session = Session()
        professor_id = self.table_professor.currentRow() + 1  # ID baseado na linha
        nome = self.input_nome_professor.text()
        nascimento = self.input_birth_professor.text()
        cpf = self.input_cpf_professor.text()
        curso = self.input_curso_professor.text()
        professor = session.query(Professor).filter_by(id=professor_id).first()
        if professor:
            try:
                professor.fullname = nome
                professor.datanascimento = datetime.strptime(nascimento, "%d-%m-%Y").date()
                professor.cpf = cpf
                professor.curso = curso
                session.commit()
                self.read_professor()  #Atualiza a tabela
            except Exception as e:
                print(f"Erro ao atualizar professor: {e}")
                session.rollback()
        session.close()

    def delete_professor(self):
        session = Session()
        professor_id = self.table_professor.currentRow() + 1  #ID baseado na linha
        professor = session.query(Professor).filter_by(id=professor_id).first()
        if professor:
            try:
                session.delete(professor)
                session.commit()
                self.read_professor()  # Atualiza a tabela
            except Exception as e:
                print(f"Erro ao deletar professor: {e}")
                session.rollback()
        session.close()
    
    # Função para Criar um Usuário
    def create_usuario(self):
        username = self.input_username.text()
        password = self.input_password.text()
        role = self.input_role.currentText()

        if username and password and role:
            # Criando o objeto Usuario
            new_user = Usuario(username=username, password=password, role=role)

            # Adicionando ao banco de dados
            session = Session()
            session.add(new_user)
            session.commit()

            self.update_user_table()  # Atualiza a tabela para exibir o novo usuário
            self.result_label.setText(f'Usuário {username} criado com sucesso!')  # Exibe a mensagem de sucesso
        else:
            self.result_label.setText("Por favor, preencha todos os campos.")  # Exibe mensagem de erro


    #funções para Curso
    def init_curso_tab(self):
        layout = QtWidgets.QVBoxLayout()

        #inputs de Curso
        self.input_nome_curso = QtWidgets.QLineEdit()
        self.input_nome_curso.setPlaceholderText("Nome do Curso")

        #botões CRUD para Curso
        self.btn_create_curso = QtWidgets.QPushButton("Criar Curso")
        self.btn_read_curso = QtWidgets.QPushButton("Ler Cursos")
        self.btn_update_curso = QtWidgets.QPushButton("Atualizar Curso")
        self.btn_delete_curso = QtWidgets.QPushButton("Deletar Curso")

        #tabela para exibir os Cursos
        self.table_curso = QtWidgets.QTableWidget()
        self.table_curso.setColumnCount(1)
        self.table_curso.setHorizontalHeaderLabels(["Nome"])

        #Layout de inputs e botões
        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Nome:", self.input_nome_curso)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_create_curso)
        button_layout.addWidget(self.btn_read_curso)
        button_layout.addWidget(self.btn_update_curso)
        button_layout.addWidget(self.btn_delete_curso)

        # ,onta o layout da aba Curso
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_curso)
        self.tab_curso.setLayout(layout)

        #Conectar botões às funções CRUD de Curso
        self.btn_create_curso.clicked.connect(self.create_curso)
        self.btn_read_curso.clicked.connect(self.read_curso)
        self.btn_update_curso.clicked.connect(self.update_curso)
        self.btn_delete_curso.clicked.connect(self.delete_curso)

    def create_curso(self):
        session = Session()
        nome = self.input_nome_curso.text()

        try:
            curso = Curso(name=nome)
            session.add(curso)
            session.commit()
            self.update_curso_combobox()
            self.read_curso()  #Atualiza a tabela
            self.clear_inputs(self.input_nome_curso)
        except Exception as e:
            print(f"Erro ao criar curso: {e}")
            session.rollback()
        finally:
            session.close()

    def read_curso(self):
        session = Session()
        cursos = session.query(Curso).all()
        self.table_curso.setRowCount(0)  #Limpa a tabela antes de preencher
        for curso in cursos:
            row_position = self.table_curso.rowCount()
            self.table_curso.insertRow(row_position)
            self.table_curso.setItem(row_position, 0, QtWidgets.QTableWidgetItem(curso.name))
        session.close()

    def update_curso(self):
        session = Session()
        curso_id = self.table_curso.currentRow() + 1  #ID baseado na linha
        nome = self.input_nome_curso.text()
        curso = session.query(Curso).filter_by(id=curso_id).first()
        if curso:
            try:
                curso.name = nome
                session.commit()
                self.update_curso_combobox()
                self.read_curso()  #Atualiza a tabela
            except Exception as e:
                print(f"Erro ao atualizar curso: {e}")
                session.rollback()
        session.close()

    def delete_curso(self):
        session = Session()
        curso_id = self.table_curso.currentRow() + 1  #ID baseado na linha
        curso = session.query(Curso).filter_by(id=curso_id).first()
        if curso:
            try:
                session.delete(curso)
                session.commit()
                self.read_curso()  #Atualiza a tabela
            except Exception as e:
                print(f"Erro ao deletar curso: {e}")
                session.rollback()
        session.close()

    def clear_inputs(self, *inputs):
        for input_field in inputs:
            input_field.clear()

####################################

    def start_transaction(self):
        self.transaction_session = Session()
        print("Transação iniciada.")

    def commit_transaction(self):
        if hasattr(self, 'transaction_session'):
            try:
                self.transaction_session.commit()
                print("Transação confirmada.")
            except Exception as e:
                print(f"Erro ao confirmar transação: {e}")
            finally:
                self.transaction_session.close()
                del self.transaction_session

    def rollback_transaction(self):
        if hasattr(self, 'transaction_session'):
            self.transaction_session.rollback()
            print("Transação desfeita.")
            self.transaction_session.close()
            del self.transaction_session

    def intersecao_alunos_professores(self):
        session = Session()
        alunos_cpfs = {aluno.cpf for aluno in session.query(Aluno).all()}
        professores_cpfs = {professor.cpf for professor in session.query(Professor).all()}
        intersecao = alunos_cpfs.intersection(professores_cpfs)
        print("Interseção de CPFs:", intersecao)
        session.close()

###############################################################

    # Função para Ler (Exibir) Usuário(s)
    def read_usuario(self):
        username = self.input_username.text()

        # Conectar à sessão do banco de dados
        session = Session()

        if username:  # Ler um usuário específico
            user = session.query(Usuario).filter_by(username=username).first()
            if user:
                self.result_label.setText(f'ID: {user.id}\nUsername: {user.username}\nRole: {user.role}')
            else:
                self.result_label.setText("Usuário não encontrado.")
        else:  # Exibir todos os usuários
            users = session.query(Usuario).all()
            self.update_user_table(users)

    # Função para Atualizar um Usuário
    def update_usuario(self):
        username = self.input_username.text()
        new_role = self.input_role.currentText()

        # Conectar à sessão do banco de dados
        session = Session()

        user = session.query(Usuario).filter_by(username=username).first()

        if user:
            user.role = new_role
            session.commit()
            self.result_label.setText(f'Usuário {username} atualizado para o role {new_role}.')
            self.update_user_table()  # Atualiza a tabela com a alteração
        else:
            self.result_label.setText("Usuário não encontrado.")

    # Função para Excluir um Usuário
    def delete_usuario(self):
        username = self.input_username.text()

        # Conectar à sessão do banco de dados
        session = Session()

        user = session.query(Usuario).filter_by(username=username).first()

        if user:
            session.delete(user)
            session.commit()
            self.result_label.setText(f'Usuário {username} excluído com sucesso!')
            self.update_user_table()  # Atualiza a tabela após a exclusão
        else:
            self.result_label.setText("Usuário não encontrado.")

    # Função para Atualizar a Tabela de Usuários
    def update_user_table(self, users=None):
        if users is None:
            session = Session()
            users = session.query(Usuario).all()

        self.table_usuario.setRowCount(len(users))  # Define o número de linhas da tabela

        for row, user in enumerate(users):
            self.table_usuario.setItem(row, 0, QtWidgets.QTableWidgetItem(user.username))
            self.table_usuario.setItem(row, 1, QtWidgets.QTableWidgetItem(user.password))
            self.table_usuario.setItem(row, 2, QtWidgets.QTableWidgetItem(user.role))



#Executando a aplicação
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CrudApp()
    window.show()
    sys.exit(app.exec_())
