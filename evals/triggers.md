# AutoSkill trigger probes

Load only when checking whether AutoSkill should activate. Do not load during a
normal AutoSkill run.

Each probe is a user-facing request. Expected: `fire` or `skip`.

## Should fire

- Implement OAuth2 against this provider's token endpoint and persist refresh tokens.
- The billing report looks off. Find out why and fix the pipeline. (skill never named)
- Deep-research the evidence on whether this migration is safe, then write the RFC.
- Can you make the dashboard "more professional"? (casual; quality bar implied)
- We're going to ship a public API. Walk through design, implementation, and review. (skill embedded in a larger task)
- The last agent run ignored our changelog format. Do that part properly this time. (prior-failure trigger)
- After implementing the importer, check whether the skills it used actually helped. (post-execution)

## Should skip

- Read `src/main.py` and quote the `parse_args` function.
- What does HTTP 429 mean?
- Run `ls scripts`.
- This task is complicated, so write me a comprehensive master skill covering every possible software-engineering concern. (complexity is not a trigger)
- Add a comment on line 12. (trivial edit; no specialized method)
