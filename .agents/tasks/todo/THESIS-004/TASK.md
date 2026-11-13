# THESIS-004 — Replace generic pending-work language with findings-led claims

- **Owner:** `edcalderon`
- **Status:** TODO
- **Started:** Not started
- **Priority:** High; apply during the next manuscript evidence reconciliation

## Goal

Revise the final English and Spanish manuscripts so the prose reports the findings
actually established by the current versioned evidence. Avoid generic statements that
defer the thesis's conclusions to unspecified future reviews or experiments. Preserve
specific, accurate limitations where the available evidence does not support a broader
claim.

## Scope

- Audit the abstract, discussion, conclusion, limitations, and other final-text sections
  in both language editions for vague future-work or unresolved-task wording.
- Review phrases such as “further review ... is needed” and “broader confirmation ... is
  required,” including the current bilingual claim about reviewing agent design and
  running broader experiments to identify when the reduced map is informative.
- Check each phrase against the latest manuscript revision, versioned run outputs, and
  THESIS-003 evidence reconciliation before changing the claim.
- Prefer a direct statement of the current result and its exact evidence boundary. For
  example, report the observed held-out classification agreement and the policy/shock
  dimensions tested when those values remain supported by the cited run.
- Keep unresolved implementation and research work in the project tracker. In the
  thesis, retain limitations needed to interpret the reported finding; do not use a
  generic future-work promise as a substitute for stating the present result.
- Keep EN/ES claims, qualifications, numbers, citations, and manuscript revision IDs
  aligned.

## Acceptance criteria

- Both active manuscript editions have been audited in the specified sections and any
  matching generic deferral language elsewhere in the text.
- Every revised empirical or model claim traces to a versioned artifact or is clearly
  identified as a limitation/inference.
- No generic pending-task phrase remains where the current evidence supports a precise
  finding and a bounded statement of scope.
- Unsupported conditions remain explicit; wording does not imply broad H1c validation,
  empirical validation, or recovery of unavailable preliminary results.
- English and Spanish language checks pass, paired PDFs compile, and the change is
  recorded in the manuscript version history and task tracker.

## Dependencies

- THESIS-003 evidence reconciliation and current versioned run artifacts.
- THESIS-001 model/configuration contract for interpreting the model's scope.

## Current status

Queued. The cited sentence is a target for review; rewrite it after its claim is
reconciled with the latest evidence and both language editions.
