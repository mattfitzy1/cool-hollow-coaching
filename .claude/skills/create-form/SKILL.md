---
name: create-form
description: Plan and build a Google Form end-to-end. Use when the user wants a questionnaire, survey, discovery form, or any Google Form they'd send to someone. The skill designs the questions with the user interactively, writes a YAML spec, and creates the form in Google Drive via the Forms API — no console clicks required. Trigger words: "create a form", "build a questionnaire", "discovery questionnaire", "Google Form", "make a survey".
---

# Create Form — Google Forms from YAML spec

Plan and build a Google Form inside the workspace. User says what they want, Claude designs it together with them, writes a spec, runs the builder, and the form shows up in your Drive with a link returned.

**No console clicks, no Apps Script copy-paste.** The form is created via Google Forms API using a service account you configure. Forms are owned by the service account and shared as editor with you (and anyone else specified), so they appear in your "Shared with me" and you have full edit rights.

---

## When to use this skill

- User asks for a Google Form, discovery questionnaire, or survey
- User wants a structured form (not freeform notes) to send to someone
- User wants a form with multiple sections, different question types, or a specific format (e.g. A/B/C + Other multiple choice)

If the user just wants a rough list of questions as a text doc, don't use this skill — use a normal markdown/docx doc.

---

## Workflow

### 1. Plan interactively

Walk through with the user:
- **Who is the audience?** (affects tone, length, which questions)
- **What's the goal?** (discovery, ROI capture, feedback, etc.)
- **Section structure** — group questions into themed sections
- **Question types per section** — paragraph (long text), short_answer, multiple_choice, checkbox, grid, scale
- **Multiple choice format** — the default is A/B/C labels + D "Other, please specify" (the `other: true` flag auto-adds D)
- **Preamble/intro text** — at the top of the form; can be warm or formal
- **Sensitive sections** — e.g. financials — flag these for a separate section with a guard-lowering preamble
- **Where to save** — Drive folder ID (optional; defaults to My Drive root)
- **Who to share with** — list of emails (at minimum your own account as editor)

Save questions as a YAML spec in `.claude/skills/create-form/specs/<name>.yaml`. Show the user a preview before running.

### 2. Build and deploy

Run:
```
python3 .claude/skills/create-form/create_form.py \
  --spec .claude/skills/create-form/specs/<name>.yaml
```

The script:
1. Reads the YAML spec
2. Calls Forms API — creates form, adds all items via `batchUpdate`
3. Moves the form into the target Drive folder (if set)
4. Shares the form with each email in `share_with` (editors)
5. **Always sets the form to "anyone with the link" can respond** (`make_public`) so external recipients are never blocked
6. Prints the form URL

To repair an existing org-locked form (created before this was enforced):
`python3 create_form.py --make-public <FORM_ID>`

Tell the user the URL. Remind them the form is in **Shared with me** (not My Drive root) because it's owned by the service account — that's expected.

### 3. Send

Offer to draft an intro email to the recipient with the form link. The recipient doesn't need a Google account — `make_public` sets the form to "anyone with the link can respond" at creation, so external recipients are never blocked.

---

## YAML spec format

```yaml
title: "Form title as it appears in Forms UI"
description: |
  Multi-line intro text that appears at the top of the form.
  Keep warm, tell them how long it'll take, tell them it's okay
  to skip questions.

settings:
  progress_bar: true
  allow_edit: true          # respondents can edit after submitting
  collect_email: false      # don't ask for respondent email unless you need to

drive_folder_id: "1abc..."  # optional — where to move the form after creation
share_with:
  - email: you@example.com
    role: writer            # writer = editor, reader = view only
  - email: someone.else@example.com
    role: writer

sections:
  - title: "Section 1 — Title"
    description: |
      Optional section preamble. Use this for sensitive sections like financials.
    items:
      - type: paragraph_text
        title: "Q1. Long-form question?"
        help: "Optional helper text under the question"
        required: false

      - type: short_answer
        title: "Q2. One-line question?"
        required: false

      - type: multiple_choice
        title: "Q3. Pick one"
        choices:
          - "A. Option one"
          - "B. Option two"
          - "C. Option three"
        other: true            # adds D. Other, please specify (free text)
        required: false

      - type: checkbox
        title: "Q4. Pick multiple"
        choices:
          - "Option A"
          - "Option B"
          - "Option C"
        other: true
        required: false

      - type: scale
        title: "Q5. Rate on 1-5"
        min: 1
        max: 5
        min_label: "Terrible"
        max_label: "Excellent"
        required: false

      - type: grid
        title: "Q6. Matrix question"
        rows:
          - "Task 1"
          - "Task 2"
        columns:
          - "Under 10%"
          - "10-25%"
          - "25%+"
        required: false
```

---

## Authentication & one-time setup

The skill uses a Google service account JSON you provide (path set via `GOOGLE_APPLICATION_CREDENTIALS` in `.env`). Two requirements on your own GCP project:

1. **Forms API enabled** on your GCP project. One-time click in the API console (Google Forms API → Enable).
2. **Drive API enabled** on the same project.

If the script returns `SERVICE_DISABLED` / "Google Forms API has not been used", tell the user to click the link above, then rerun.

---

## Default conventions

- **Multiple choice format:** A/B/C lettered options + D "Other, please specify". The `other: true` flag on any `multiple_choice` or `checkbox` item activates Forms' built-in "Other" option.
- **Financial sections** always include a preamble explaining why the numbers are asked (ROI prioritisation) and reassuring that any question can be skipped.
- **No required fields** on discovery questionnaires. Respondents should be free to skip.
- **Language:** UK English.

---

## Notes

- Forms are owned by the service account. You get editor access via the `share_with` list. They appear under **Shared with me** in Drive, not under **My Drive**.
- To move a form to your own ownership: transfer ownership manually from the Forms UI (File → Share → change owner). Do this only if needed.
- Response collection: forms auto-collect responses in Forms' own UI. To pipe responses to a Google Sheet, add `response_sheet: true` in the YAML spec (the script will create a linked Sheet and share it).
