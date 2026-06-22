---
name: develop
description: "Develop a content idea stub into a fully strategised, packaged social concept in the brand's voice"
---

# /develop: Develop Content Concept

> Take a content idea stub and develop it into a fully strategised, packaged social concept in the brand's voice.

## Variables

idea: $ARGUMENTS (the stub ID like "#5", or a raw idea to capture and develop in one go)

## Instructions

You are running the **Develop** step of the Content Pipeline. Your job is to take a captured idea and turn it into a fully developed social concept: strategic positioning, audience alignment, packaging (hook, on-screen text, caption, hashtags, carousel concept), and the soft path to the offer.

Everything you write is in **the brand's voice** as captured in `context/voice-and-tone.md` and `context/brand.md`. No hype, no generic filler, no words the voice profile flags as off-brand. Read `context/voice-and-tone.md` and let it set the tone for every line.

### Setup: Load Context

1. **Read the idea:**
   - If given an ID (#N): query `SELECT * FROM content_ideas WHERE id = N` via the content database
   - If given raw text: this is a new idea, capture it as a stub first (classify channel + format), then develop

2. **Read the content strategy docs** (ALWAYS read these):
   - `content/strategy.md`, the platform, cadence, pillars, and audience
   - `content/brand-and-audience.md`, brand positioning, audience, visual + tone anchors, the words to avoid
   - `content/offers-and-funnels.md`, the offers and how content points at them

3. **Read the voice profile:**
   - `context/voice-and-tone.md`, the brand's actual voice. This wins over any generic phrasing.

4. **Check the recent pipeline** (so you don't repeat what's already queued or just posted):
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys; sys.path.insert(0, '.')
   from scripts.context_aggregator import build_context_window, format_context_for_prompt
   context = build_context_window()
   print(format_context_for_prompt(context))
   "
   ```
   Read the output, it tells you what's already been published recently and what's already in the pipeline (stubs, developed, scheduled). Use it to avoid overlap and to angle the new piece against what came before.

### Stage 1: STRATEGIC POSITIONING (Present and confirm)

Using the idea + recent pipeline + strategy docs, develop the strategic frame:

1. **Audience alignment**: Which reader does this serve? What does it give them?
2. **Content pillar**: Which content pillar does this sit under (from `content/strategy.md`)?
3. **Brand fit**: Why is this on-brand? How does it sit in the brand's register?
4. **Offer path**: How does this point softly toward the offer? Keep it implicit unless it's an offer-focused piece.
5. **Narrative fit**: How does this connect to what's been posted recently? (Reference the recent pipeline.)

**STOP. Present the strategic frame concisely. Ask: "Does this positioning feel right? Any angle changes?"**

### Stage 2: PACKAGING (Present and confirm)

Package it for the chosen platform. Pick the format that fits the idea (reel, carousel, still, or story) and build the matching pieces:

1. **Reel hook (3-5 options)**: The first line said or shown in the first second. Each should stop the scroll without shouting. Intriguing, not clickbait. (Most relevant for reels; for a still or carousel, this is the opening caption line instead.)
2. **On-screen text**: The short text overlaid on the reel or the lead slide. 2-6 words, complementary to the spoken or caption line, not a repeat of it.
3. **Caption**: Written fully in the brand's voice. A strong opening line (the first line carries the post), the body, and a soft CTA toward the offer where it fits. No words the voice profile flags as off-brand, no em dashes.
4. **Hashtags (5-10)**: A blend of topic and brand-adjacent tags. Relevant, not spammy.
5. **Carousel concept** (if a carousel), Slide-by-slide: one idea per slide, the order, and the through-line. Stay on the brand's visual system, one clear thought per slide.

Make packaging **complementary**: the on-screen text and the caption should add to each other, not say the same thing. Reference the visual anchors in `content/brand-and-audience.md` so any image direction stays on-brand.

**STOP. Present packaging options. Ask: "Which direction feels strongest? Any adjustments?"**

### Stage 3: STORE & FINALISE

After the owner confirms:

1. **Assign a priority score (1-10):**
   - Brand value (does it build the right belief?)
   - Usefulness (does it give the reader something real?)
   - Timeliness (a seasonal or moment hook?)
   - Production effort (how much to film or design?)
   - Gap (not already covered recently, check the pipeline)

2. **Write to database:**
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys, json; sys.path.insert(0, '.')
   from scripts.content_db import get_connection
   from scripts.content_writer import write_developed_idea

   idea = {
       'id': EXISTING_ID_OR_NONE,
       'title': 'Short working title',
       'hook': 'Chosen reel hook / opening line',
       'description': 'Full concept description',
       'audience': 'Which reader this serves',
       'format_type': 'reel',          # reel | carousel | still | story
       'channel': 'instagram',
       'topics': 'comma,separated,topics',
       'source_type': 'develop',
       'title_options': json.dumps([
           {'text': 'Hook A', 'elements': ['clear', 'useful']},
           {'text': 'Hook B', 'elements': ['curiosity', 'story']},
       ]),
       'thumbnail_concepts': json.dumps([
           {'on_screen_text': '2-6 words', 'visual': 'on-brand framing'},
       ]),
       'funnel_position': 'awareness',
       'content_pillar': 'PILLAR',
       'audience_segment': 'SEGMENT',
       'offer_alignment': 'OFFER | none',
       'cta_path': 'Soft CTA toward the offer',
       'proof_points': json.dumps([]),    # only real, confirmed proof, never invent
       'authority_angle': 'Why the brand owns this',
       'production_status': 'developed',
       'priority_score': 8,
       'research_json': json.dumps({}),
       'developed_by': 'develop',
   }

   conn = get_connection()
   idea_id = write_developed_idea(conn, idea)
   conn.close()
   print(f'Saved as concept #{idea_id}')
   "
   ```

3. **Write the concept doc:**
   Save the full concept to `content/concepts/{id}-{slug}.md` with the positioning, the chosen hook, on-screen text, the full caption, hashtags, and the carousel concept if any.

4. **Regenerate the pipeline:**
   ```bash
   source .venv/bin/activate && python3 scripts/generate_pipeline.py
   ```

5. **Report:**
   - Saved as concept #ID
   - Concept doc written to `content/concepts/`
   - The chosen hook + format + pillar
   - Priority score
   - "Ready for scheduling. Run /schedule when you want to plan your week."

### Critical Rules

- **Interactive**: Present positioning, wait for confirmation. Present packaging, wait for confirmation. Never blast through all stages at once.
- **Brand voice always**: Every line of copy is the brand's voice from `context/voice-and-tone.md`. If a draft drifts off-brand, rewrite it.
- **One platform per concept**: Pick the platform and stick to it. The format choice is reel, carousel, still, or story.
- **Complementary packaging**: On-screen text and caption give different information.
- **Soft path to the offer**: Every piece can lead toward the offer, but keep it implicit unless it's an offer-focused piece.
- **Never invent proof**: No made-up results, numbers, or testimonials in captions or copy.
- **Avoid off-brand words**: stay clear of anything the voice profile flags. No em dashes.
