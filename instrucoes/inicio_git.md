# Configuração do Git e SSH no Windows para GitHub

Este guia descreve os passos para instalar o Git, configurá-lo e gerar uma chave SSH para autenticação com o GitHub no Windows.

## 1. Instalar o Git

Baixe e instale o Git para Windows a partir do site oficial:
[https://git-scm.com/install/windows](https://git-scm.com/install/windows)

(Abra o "Git Bash", "cmd" ou "powershell" para executar os próximos comandos).

## 2. Configurar o Usuário do Git

Configure seu nome de usuário e e-mail globalmente. Estes dados serão usados em seus commits.

**Importante:** Substitua `"User"` e `"User@mail.br"` pelo seu nome de usuário e e-mail reais do GitHub.

```bash
git config --global user.name "User"
git config --global user.email "User@mail.br"
````

## 3\. Gerar Chave de Acesso SSH

Gere uma nova chave SSH usando o algoritmo `ed25519`.

```bash
ssh-keygen -t ed25519 -C "User@mail.br"
```

  * Quando solicitado, pressione Enter para aceitar o local padrão do arquivo.
  * Recomenda-se definir uma senha (passphrase) para sua chave quando solicitado.

## 4\. Configurar o Agente SSH (PowerShell)

Abra o **PowerShell como Administrador** para executar os comandos a seguir.

### Ativar o Agente SSH do Windows

Isso garante que o serviço `ssh-agent` inicie automaticamente e esteja em execução.

```powershell
# Define o serviço para iniciar automaticamente
Get-Service ssh-agent | Set-Service -StartupType Automatic

# Inicia o serviço
Start-Service ssh-agent
```

### Adicionar a Chave SSH ao Agente

Vincule a chave SSH recém-criada ao agente SSH do Windows.

```powershell
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

  * Se você definiu uma senha (passphrase) no passo 3, ela será solicitada agora.

### Confirmar Carregamento da Chave

Verifique se a chave foi carregada com sucesso.

```powershell
ssh-add -l
```

## 5\. Adicionar a Chave ao GitHub

Consulte sua chave pública. O resultado deste comando deve ser copiado.

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

1.  Copie todo o texto exibido (que começa com `ssh-ed25519...`).
2.  Acesse sua conta do GitHub e vá para **Settings**.
3.  No menu lateral, clique em **SSH and GPG keys**.
4.  Clique no botão **New SSH key**.
5.  Dê um "Title" (Título) descritivo para a chave (ex: "Meu PC Windows").
6.  Cole a chave copiada no campo "Key".
7.  Clique em **Add SSH key**.

## 6\. Testar a Conexão

Após adicionar a chave ao GitHub, teste a conexão no seu terminal (Git Bash ou PowerShell).

```bash
ssh -T git@github.com
```

Você deverá ver a seguinte mensagem de sucesso (substituindo "user" pelo seu nome de usuário):

```
Hi user! You've successfully authenticated, but GitHub does not provide shell access.
```

```
```
