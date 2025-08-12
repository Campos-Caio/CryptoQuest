#  CryptoQuest

CryptoQuest é uma plataforma educacional gamificada, projetada para ensinar conceitos sobre criptomoedas e blockchain de forma interativa e acessível. Utilizando uma abordagem de "aprender jogando", o aplicativo guia os usuários através de uma jornada de conhecimento com missões, quizzes e recompensas.

## Funcionalidades

- **Autenticação Completa:** Cadastro e Login com E-mail/Senha e Google.
- **Onboarding Personalizado:** Questionário inicial para avaliar o nível de conhecimento do usuário.
- **Fluxo de Navegação Inteligente:** Redirecionamento automático pós-login para o questionário ou para a tela principal.
- **Perfil de Usuário:** Visualização e edição de informações do perfil (nome, bio, etc.).
- **Backend Robusto e Testado:** API desenvolvida em FastAPI com uma suíte de testes automatizados (unitários e de integração).

## 🚀 Tecnologias Utilizadas

| Categoria | Tecnologia |
| :--- | :--- |
| **Backend** | Python, FastAPI, Pydantic, Pytest |
| **Frontend** | Flutter, Provider |
| **Banco de Dados** | Google Firestore |
| **Autenticação** | Firebase Authentication |

## 🔧 Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas:
- Flutter SDK (versão 3.0 ou superior)
- Python (versão 3.10 ou superior)
- Git
- Uma conta no [Firebase](https://firebase.google.com/) com um projeto criado.
- VS Code (ou outro editor de sua preferência).

## ⚙️ Configuração do Ambiente

Siga os passos abaixo para configurar e rodar o projeto localmente.

### **Backend (Servidor FastAPI)**

1.  **Clone o repositório e acesse a pasta do backend:**
    ```
    git clone [https://github.com/Campos-Caio/CryptoQuest.git](https://github.com/Campos-Caio/CryptoQuest.git)
    cd CryptoQuest/backend
    ```

2.  **Adicione as Credenciais do Firebase:**
    - No console do Firebase, vá em `Configurações do Projeto > Contas de serviço`.
    - Gere uma nova chave privada e baixe o arquivo `.json`.
    - Coloque este arquivo na raiz da pasta `backend/`.

3.  **Crie e Ative o Ambiente Virtual (`venv`):**
    ```
    # Criar
    python -m venv venv

    # Ativar no Windows (PowerShell)
    .\venv\Scripts\activate
    ```
    *Se o PowerShell bloquear a execução, rode primeiro: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`*

4.  **Instale as Dependências:**
    ```
    pip install -r requirements.txt
    ```

5.  **Rode o Servidor:**
    ```
    uvicorn app.main:app --reload
    ```
    O servidor estará disponível em `http://127.0.0.1:8000`.

### **Frontend (Aplicativo Flutter)**

1.  **Acesse a pasta do frontend:**
    ```
    # A partir da raiz do projeto
    cd frontend/cryptoquest
    ```
2.  **Configure o Firebase no Flutter:**
    - Utilize a CLI do FlutterFire para conectar o app ao seu projeto Firebase:
      ```
      flutterfire configure
      ```
    - Isso irá gerar o arquivo `lib/firebase_options.dart` automaticamente.

3.  **Instale as Dependências do Flutter:**
    ```
    flutter pub get
    ```

4.  **Rode o Aplicativo:**
    - Inicie um emulador ou conecte um dispositivo.
    - Execute o comando:
      ```
      flutter run
      ```

---
## 🧪 Como Testar o Sistema

### **Testes Automatizados do Backend**

O backend possui uma suíte de testes para garantir sua estabilidade.

1.  Acesse a pasta `backend/` e ative o `venv`.
2.  Execute todos os testes:
    ```
    pytest
    ```
3.  Para rodar os testes de um arquivo específico:
    ```
    pytest tests/api/test_user_api.py
    ```
**Resultado Esperado:** Todos os testes devem passar, indicando que a lógica e os endpoints estão funcionando corretamente.

### **Teste Manual do Fluxo Completo (End-to-End)**

Com o backend e o frontend rodando, siga a jornada do usuário:

1.  **Cadastro:** Crie um novo usuário no aplicativo.
2.  **Login:** Acesse a conta recém-criada.
3.  **Questionário:** Você será automaticamente redirecionado para o Questionário Inicial. Responda e envie.
4.  **Navegação para a Home:** Após o envio, você deve ser redirecionado para a `HomePage`.
5.  **Acesso e Edição do Perfil:**
    - Abra o menu lateral (`Drawer`) e acesse "Meu Perfil".
    - Altere seu nome e adicione uma biografia.
    - Clique em "Salvar Alterações" e verifique se as informações foram atualizadas.
6.  **Logout:** Utilize o botão de sair e confirme que você retornou à tela de Login.

## 👨‍💻 Autor

- **Caio Alves Campos**
