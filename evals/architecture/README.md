# Evals for the architecture plugin

Cases for the proof of concept. Each case has a `prompt.md` (what the agent receives) and a `grader.md` (PASS/FAIL criteria a judge applies).

## Method (taken from proyecto26/system-design-skills, adapted)

1. **Calibrate the judge** before anything else: give it a strong answer and a deliberately bad one for the same case. If it does not separate them clearly, the judge is useless.
2. **With and without skills**: run each case with the `architecture` plugin installed and without it (baseline), with the same model.
3. **n = 3** runs per configuration; report the mean and the deviation, not a single result.
4. **Check the composition**: that the skills were really invoked (for example, that the capacity came from the script and not from memory).
5. Also report where the baseline won. An eval that always proves the skills right measures nothing.

The prompts are in English; to check that the skills answer in the user's language, run a case translated into another language and check the answer's language.

| Case | What it measures |
|---|---|
| 01 over-decomposition trap | YAGNI: not proposing microservices + Kafka at a tiny scale |
| 02 legacy migration | Step 0, design as a delta, migration path with doors, legacy as the oracle |
| 03 measured capacity | Correct calculation from metrics (Little, utilization), with the script |
| 04 dependency brownout | Retry amplification, pool exhaustion, metastable state, detection |
| 05 legacy partner integration | Strategic design: ACL vs Conformist, Published Language, transition |
| 06 exploratory without metrics | Designing without data from the archetype: invariants first, scenarios and thresholds, PoC plan |
