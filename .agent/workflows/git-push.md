---
description: Fazer commit e push para GitHub com mensagem profissional
---

# Workflow: Git Push Profissional

Este workflow permite fazer commits profissionais seguindo o padrão Conventional Commits.

## Pré-requisitos
- Git instalado e configurado
- Repositório conectado ao GitHub

## Passos

### 1. Verificar alterações pendentes
```powershell
git status
```

### 2. Adicionar arquivos ao staging
```powershell
git add .
```

### 3. Fazer commit com mensagem profissional
Use um dos prefixos:
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `refactor:` - Refatoração
- `perf:` - Performance

```powershell
git commit -m "TIPO: descrição clara e técnica da alteração"
```

Exemplos:
- `git commit -m "feat: adiciona integração com Evolution API para WhatsApp"`
- `git commit -m "fix: resolve timeout na geração do QR Code"`
- `git commit -m "docs: atualiza documentação do projeto"`

### 4. Enviar para o GitHub
// turbo
```powershell
git push
```

### 5. (Opcional) Criar Pull Request
Acesse o GitHub para criar um PR se estiver trabalhando em branch separada.
