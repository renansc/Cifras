# NanotechSoft-Cifras v8.2

Esta versao adiciona exclusao individual e em lote na interface:

- **GERENCIAR CIFRAS**: marque uma ou mais cifras e use **EXCLUIR SELECIONADAS**.
- **SELECIONAR VISIVEIS**: marca ou desmarca apenas o resultado atual da busca.
- **GERENCIAR REPERTORIOS**: marque um ou mais repertorios e use **EXCLUIR SELECIONADOS**.
- A exclusao de repertorios preserva as cifras por padrao e oferece uma segunda
  confirmacao para remover as que ficarem orfas.
- **LIMPAR ORFAS** remove cifras que nao pertencem a nenhum repertorio.
- A exclusao de cifras tambem remove seus vinculos com repertorios e suas
  anotacoes locais.

Todas as operacoes destrutivas exigem confirmacao. Exporte um backup antes de
uma limpeza grande.

O recurso foi implementado em `app/gerar_v4.py`; portanto, executar
`./gerar.sh` conserva os controles na proxima geracao. A aplicacao pronta fica
em `saida/NanotechSoft-Cifras.html`, com uma copia em `cifras.html`.
