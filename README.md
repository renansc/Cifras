# NanotechSoft-Cifras v8.2

Gerador de repertório offline para palco.

Entrada: `repertorio.txt`

Formato:
`Numero|Musica|Artista|Tom|URL|Semitons`

Exemplo:
`34|Jeito Carinhoso|Aviões do Forró|Em|URL_DA_CIFRA|-3`

## Instalar
```bash
sudo apt update
sudo apt install python3 python3-bs4
```

## Gerar
```bash
chmod +x gerar.sh compactar_saida.sh
./gerar.sh
xdg-open saida/NanotechSoft-Cifras.html
```

O arquivo `cifras.html` da raiz e uma copia pronta da mesma aplicacao. Depois de
gerar novamente, use sempre `saida/NanotechSoft-Cifras.html` como resultado
principal.

## Excluir cifras e repertorios

No menu 3D, abra **GERENCIAR CIFRAS**. Cada cifra possui a acao **EXCLUIR**. Para apagar
varias de uma vez, marque as caixas, use **SELECIONAR VISIVEIS** se necessario
e clique em **EXCLUIR SELECIONADAS**. A busca limita quais cifras o botao de
selecao marca. A exclusao tambem retira as cifras dos repertorios e remove suas
anotacoes locais, sempre depois de confirmacao.

Em **GERENCIAR REPERTORIOS**, cada repertorio possui **EXCLUIR**. Para exclusao em lote,
marque as caixas e clique em **EXCLUIR SELECIONADOS**. As cifras permanecem na
biblioteca por padrao; uma segunda confirmacao permite remover somente as que
ficarem sem nenhum repertorio.

O botao **LIMPAR ORFAS** remove cifras que ja nao pertencem a repertorio algum.
Faca backup antes de exclusoes em lote, pois elas nao podem ser desfeitas.

## Gerar ZIP do repertório pronto
```bash
./compactar_saida.sh
```

A saída tem busca, anterior/próxima, modo claro/escuro, A-/A+, anotações por linha e exportação/importação das anotações.

A música sem URL ou cujo site bloquear download aparece como PENDENTE. O programa não tenta contornar 403, CAPTCHA ou login.

Para tablet, copie/descompacte a pasta de saída localmente e abra `index.html`. Para show, isso é mais confiável que depender de abrir os HTML diretamente da nuvem.

As anotações ficam no armazenamento local do navegador. Use Exportar/Importar notas para backup e transferência.


## Backup v2

Na tela principal (`index.html`) existem três novos controles:

- **💾 BACKUP**: gera `backup_app_cifra_YYYY-MM-DD.json`.
- **♻ RESTAURAR**: importa um backup em outro navegador/dispositivo.
- **🗑 LIMPAR NOTAS**: apaga somente as anotações locais após confirmação.

O backup contém:
- todas as anotações de todas as músicas;
- tamanho da fonte;
- tema claro/escuro;
- data/hora;
- versão do formato.

### Notebook -> tablet

1. No notebook, abra `index.html` e clique **BACKUP**.
2. Copie a pasta/ZIP do repertório e o JSON de backup para o Google Drive.
3. No tablet, deixe o repertório disponível localmente/offline.
4. Abra `index.html`.
5. Clique **RESTAURAR** e selecione o JSON.
6. As anotações/configurações passam a valer nesse navegador do tablet.

O backup não contém as letras/cifras; elas continuam nos HTML gerados em `saida/`.


## V3 — duas formas de uso

`./gerar.sh` produz simultaneamente:

1. `saida/index.html` + páginas individuais — versão tradicional.
2. `saida/NanotechSoft-Cifras.html` — versão de arquivo único, indicada para Google Drive/tablet.

O arquivo único incorpora a logo NanotechSoft e todas as músicas geradas. Anterior/Próxima/Repertório funcionam internamente, sem depender de links para outros arquivos.

Para gerar pacotes de transporte:

```bash
./compactar_saida.sh
```

São criados:
- `NanotechSoft-Cifras_completo.zip`
- `NanotechSoft-Cifras_unico.zip`

Para Google Drive/tablet, prefira `NanotechSoft-Cifras.html` ou o ZIP `NanotechSoft-Cifras_unico.zip`.


## Publicar no GitHub

Execute `bash publicar-no-github.sh` nesta pasta. O script publica os arquivos no repositório `renansc/Cifras` e exclui backups JSON locais, para não expor dados em um repositório público.
