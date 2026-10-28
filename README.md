# Meta Vibe Coding

Meta Vibe Coding aims to help non-experts decide what software they need,
understand its consequences, and eventually own and maintain it. The objective is
a useful solution. Reuse existing ideas, tools, and components when they fit;
research publication is optional. The scope covers general vibe coding: websites,
applications, games, utilities, and automations.

The first milestone is **Level 0: Intent Interpreter**. It turns an idea into a
plain-language recommendation and a structured engineering brief. It may recommend
an existing tool or advise against building.

**Current state:** product plan, acceptance cases, and draft state/interaction
contracts. The design supports local models, commercial APIs, and wrappers around
existing coding agents through one shared contract. None is implemented yet; see
[backend options](docs/decisions.md#d007-interchangeable-inference-and-agent-backends).

## Start here

| If you want to… | Read |
| --- | --- |
| Understand the purpose and long-term vision | [Proposal](docs/meta-vibe-coding-proposal.md) |
| Know what to build first and how to assess it | [Level 0 scope](docs/level-0.md) |
| Find or claim work | [Work board](docs/work-board.md) |
| Contribute with people or agents | [Contributing](CONTRIBUTING.md) |
| Follow code, filename, and directory conventions | [Contribution standards](CONTRIBUTING.md#code-conventions) |
| Run an agent in this repository | [Agent instructions](AGENTS.md) |
| Write or revise documentation | [Writing guide](docs/writing-guide.md) |
| Understand recorded choices | [Decision log](docs/decisions.md) |

## Repository map

```text
README.md                         Project entry point and current capability
AGENTS.md                         Shared instructions for coding agents
CLAUDE.md                         Entry point to the same instructions for Claude
CONTRIBUTING.md                   Human and agent collaboration workflow
docs/meta-vibe-coding-proposal.md  Product purpose and staged delivery plan
docs/level-0.md                   Current milestone and acceptance criteria
docs/work-board.md                Shared tasks, ownership, and review evidence
docs/decisions.md                 Durable decisions and unresolved choices
docs/writing-guide.md             Documentation and product writing conventions
.github/                         Optional issue and pull request templates
```

Add source, tests, examples, and evaluation artifacts when work needs them. The
implementation task should establish their locations and exact setup, run, and
check commands here. No application setup is required for the current documents.

## First contribution

Read the Level 0 scope, check the work board, and agree on a small task with a
clear outcome. Record its owner and affected paths before editing shared files.
Use a separate branch and worktree for concurrent work when possible; see
[Contributing](CONTRIBUTING.md) for the shared-checkout alternative.

Keep the distinction between the collaboration process and the product: several
people and agents can build this repository together, while the Level 0 product
itself remains a small system without multi-agent orchestration.
