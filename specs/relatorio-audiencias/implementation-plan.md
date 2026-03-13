# Plano de Implementacao: Skill Relatorio de Audiencias

## Fase 1: Criar SKILL.md da nova skill

- [x] Criar `skills/relatorio-audiencias/SKILL.md` com:
  - [x] Frontmatter YAML (name, description com triggers)
  - [x] Persona e introducao
  - [x] Secao "Ferramentas Disponiveis" (MCP TecJustica + Skill DOCX)
  - [x] Secao "Principio de Economia"
  - [x] Workflow completo (Etapas 0-4)
  - [x] Formato de saida (tabela, complementos, processo sem audiencias, DOCX)
  - [x] Regras de Ouro (9 regras)

### Detalhes Tecnicos

Seguir exatamente o design spec em `docs/superpowers/specs/2026-03-13-relatorio-audiencias-design.md`. O SKILL.md deve seguir o mesmo padrao estrutural das skills existentes (`analise-processo-penal` e `analise-processo-civil`), adaptando para o escopo de audiencias:
- Frontmatter com description longa e rica em triggers
- Ferramentas listadas com assinaturas e descricoes
- Workflow numerado com exemplos de chamadas
- Regras de ouro numeradas
- Sem secao de visuais (escopo e tabular)
- Sem references/ (nao precisa de ritos ou modelos)

## Fase 2: Integrar com skills existentes

- [x] Adicionar secao "Skill Relatorio de Audiencias" em `skills/analise-processo-penal/SKILL.md`
- [x] Adicionar secao "Skill Relatorio de Audiencias" em `skills/analise-processo-civil/SKILL.md`

### Detalhes Tecnicos

Adicionar a seguinte secao em ambas as skills, antes da secao "Regras de Ouro":

```markdown
### Skill Relatorio de Audiencias (instalada por default)
Para relatorio completo de audiencias realizadas no processo, invoque a skill `relatorio-audiencias`. Ela retorna tabela estruturada com todas as audiencias, ouvidos, resumos e providencias.
```

## Fase 3: Validacao final

- [ ] Verificar que o SKILL.md segue o padrao das skills existentes
- [ ] Verificar que as referencias cruzadas estao corretas
- [ ] Commit final com todas as alteracoes
