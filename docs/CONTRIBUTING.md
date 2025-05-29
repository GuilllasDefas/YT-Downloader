# Guia de Contribuição

Obrigado pelo interesse em contribuir com o YouTube Downloader! Este documento fornece diretrizes e passos para contribuir com o projeto.

## Como posso contribuir?

Existem várias maneiras de contribuir com o projeto:

1. **Reportar bugs**: Reporte bugs e problemas através das issues
2. **Sugerir melhorias**: Sugira novas funcionalidades ou melhorias
3. **Contribuir com código**: Implemente correções ou novas funcionalidades
4. **Melhorar a documentação**: Ajude a melhorar a documentação do projeto
5. **Testar o aplicativo**: Teste o aplicativo em diferentes sistemas e condições

## Fluxo de trabalho para contribuições de código

### 1. Configuração

1. Faça um fork do repositório
2. Clone o fork em sua máquina local
3. Configure o repositório original como "upstream"

   ```bash
   git remote add upstream https://github.com/proprietario-original/YT-Downloader.git
   ```

4. Crie um ambiente virtual

   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   ```

5. Instale as dependências de desenvolvimento

   ```bash
   pip install -r requirements-dev.txt
   ```

### 2. Desenvolvimento

1. Crie uma branch a partir da main

   ```bash
   git checkout -b feature/sua-feature
   ```

2. Faça as alterações necessárias
3. Adicione testes para sua implementação quando aplicável
4. Execute os testes para garantir que tudo funcione
5. Atualize a documentação se necessário

### 3. Estilo de código

- Siga a PEP 8 para Python
- Use nomes descritivos para variáveis e funções
- Adicione comentários quando necessário
- Mantenha funções pequenas e com responsabilidades únicas

### 4. Commit e Push

1. Faça commits com mensagens claras e descritivas

   ```bash
   git commit -m "Adiciona funcionalidade X que resolve o problema Y"
   ```

2. Atualize sua branch com as mudanças do upstream

   ```bash
   git pull upstream main
   ```

3. Resolva qualquer conflito que possa surgir
4. Faça push para o seu fork

   ```bash
   git push origin feature/sua-feature
   ```

### 5. Pull Request

1. Abra um Pull Request (PR) no GitHub
2. Descreva claramente o que o PR faz e por que
3. Inclua capturas de tela se aplicável
4. Responda a quaisquer perguntas ou solicitações de mudança

## Reportando bugs

Ao reportar bugs, inclua:

1. Passos para reproduzir o bug
2. Comportamento esperado vs. comportamento observado
3. Versão do Python e do sistema operacional
4. Capturas de tela, se aplicável
5. Logs de erro, se disponíveis

## Sugerindo melhorias

Para sugerir melhorias:

1. Descreva claramente a melhoria
2. Explique por que essa melhoria seria útil
3. Forneça exemplos de como a melhoria funcionaria
4. Considere como ela afetaria o fluxo atual do usuário

## Perguntas?

Se tiver dúvidas sobre como contribuir, abra uma issue ou entre em contato com os mantenedores.

Obrigado por contribuir!
