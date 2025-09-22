# Sites de demonstração com IA

Este repositório foi preparado para acelerar a criação de landing pages de demonstração para potenciais clientes. A estrutura permite gerar rapidamente um site estático a partir de um arquivo JSON com as informações do negócio, aplicando automaticamente um layout moderno pronto para ser personalizado.

## Visão geral da estrutura

```
.
├── content/                # Configurações individuais de cada cliente
│   ├── assets/             # Logos e imagens utilizadas nas páginas
│   └── sample_business.json
├── scripts/
│   └── generate_site.py    # Script que converte o JSON em páginas estáticas
├── templates/
│   └── base/
│       └── style.css       # Estilos compartilhados por todos os sites
└── sites/                  # Saída gerada (um diretório por cliente)
```

## Pré-requisitos

* Python 3.9+ instalado no ambiente
* Logos ou imagens locais salvas em `content/assets/`

## Como gerar um novo site

1. **Crie o arquivo de conteúdo**: copie `content/sample_business.json` para um novo arquivo dentro da pasta `content/` (por exemplo, `content/cliente_alpha.json`). Edite os campos com as informações da empresa (cores, textos, serviços, depoimentos etc.).
2. **Ajuste o caminho da logo**: salve o arquivo da logo em `content/assets/` e informe o caminho relativo em `site.logo` (ex.: `"content/assets/logo-cliente.svg"`). O script copiará o arquivo automaticamente para a pasta final. Também é possível utilizar um endereço externo (ex.: `https://...` ou `data:`); nesse caso o arquivo não é copiado e será referenciado diretamente.
3. **Execute o gerador**:

   ```bash
   python scripts/generate_site.py content/cliente_alpha.json
   ```

   O script criará um diretório dentro de `sites/` utilizando o `slug` definido no JSON (ou gerado automaticamente a partir do nome) com os arquivos `index.html`, `style.css` e os assets necessários, limpando versões anteriores do mesmo site para evitar arquivos obsoletos.

4. **Publique**: faça o upload do conteúdo da pasta `sites/<slug>/` para a hospedagem da Hostinger (ou outra de sua preferência). O HTML é estático, então basta enviar os arquivos via FTP ou gerenciador de arquivos.

## Personalizações rápidas

* **Cores**: altere as propriedades `primary_color`, `secondary_color`, `accent_color`, `background_color` e `text_color` no bloco `site` do JSON. Esses valores alimentam as variáveis CSS usadas pelo layout.
* **Imagem de destaque**: adicione `hero.image` (apontando para um arquivo em `content/assets/`) e `hero.image_alt` para exibir uma foto ao lado do texto principal.
* **Chamadas para ação**: edite `hero.primary_cta`, `hero.secondary_cta` e `cta.button` com os links temporários ou botões de WhatsApp.
* **Portfólio visual**: utilize o bloco `showcase` para montar uma galeria de resultados com título, descrição e lista de imagens.
* **Seções opcionais**: os blocos `about`, `services`, `showcase`, `testimonials`, `faq`, `cta` e `contact` são opcionais. Se algum deles estiver vazio ou ausente, a seção correspondente não será exibida nem aparecerá na navegação.
* **Mapa e redes sociais**: em `contact.maps_link` utilize o link de incorporação do Google Maps. Em `contact.social` inclua quantos perfis forem necessários.

## Fluxo sugerido para fechar contratos

1. Encontrar empresas sem site ou com presença digital fraca.
2. Coletar logo, paleta aproximada e principais serviços/produtos.
3. Preencher rapidamente o arquivo JSON e gerar o site de demonstração.
4. Publicar a versão temporária na sua hospedagem e enviar o link personalizado ao cliente.
5. Ajustar o conteúdo em conjunto com o cliente interessado e converter o projeto em contrato.

## Próximos passos

* Criar novos templates em `templates/` caso deseje variar o layout entre setores.
* Integrar ferramentas de IA para sugerir automaticamente textos a partir de poucas palavras-chave, preenchendo o JSON.
* Versionar cada proposta em commits separados para acompanhar evolução de conteúdo.

Sinta-se à vontade para editar qualquer site dentro da pasta `sites/` manualmente após a geração, inclusive adicionando seções específicas para cada cliente.
