# Lawn cut height through the year: research for a robot mower's automation

**Date:** 1 November 2026
**Question:** How should the cut height of a cool-season lawn in southern England change through
the year, so that Home Assistant can set a robot mower's (Segway Navimow) height by itself all year?
**Setup assumed:** a robot mower cutting little and often (most days), heights 20 to 95 mm in
5 mm steps. The previous, summer-only version of this automation used a 50 mm target, 70 mm
"protective" in heat, stepped down 5 mm at a time and had no cold-season rules.

All sources accessed 1 November 2026. Where a page could not be fetched directly (blocked or
rate-limited) and the wording comes from a search-engine excerpt, that is marked "(excerpt)".

---

## Climate context

The rules below are in terms of the 7-day mean air temperature. To see when they will bite where
you are, look up your nearest station's 1991-2020 monthly averages
([Met Office climate averages](https://www.metoffice.gov.uk/research/climate/maps-and-data/location-specific-long-term-averages)).
In lowland southern England the monthly mean typically falls through 10 °C in late October and
8 °C in mid-November, and climbs back through 8 °C in early April and 10 °C in late April, with
air frosts from October to May.

---

## 1. Autumn and winter height

- **RHS, November:** "raise the cutting height to about 5mm (¼in) higher than in summer", and
  grass "continues to grow in temperatures above 7°C", so mow only on mild days
  ([RHS, November lawns](https://www.rhs.org.uk/advice/in-month/november/lawns)).
- **RHS, October:** a "slightly higher cutting height than in summer"; "Mow if necessary during
  mild weather" ([RHS, October lawns](https://www.rhs.org.uk/advice/in-month/october/lawns)).
- **RHS, how to mow:** "aim to keep grass at about 4cm (1½in) tall in spring, autumn, and winter,
  and at about 2.5cm (1in) in summer" ([RHS, how to mow a lawn](https://www.rhs.org.uk/lawns/how-to-mow-a-lawn)).
  The RHS mowing guide says the same in ranges: "13–25mm (½–1in) in summer and up to 40mm (1½in)
  in spring and autumn for ordinary domestic lawns"; in winter "mow occasionally on a high cut
  setting" ([RHS, lawn mowing](https://www.rhs.org.uk/lawns/mowing)).
- **Navimow (manufacturer blog, excerpt):** for the last mow, "Set the cutting height to
  approximately 4–5 cm. This height provides a reliable buffer against frost and prevents the
  stems from bending over", and "If the lawn is mowed below a height of approximately 3.5 cm, it
  loses some of its natural protection against the cold"
  ([Navimow UK, last mow of the year](https://uk.navimow.com/blogs/lawn-care/last-mow-of-the-year)).

**Disagreement.** RHS and Navimow say go up, or stay at about 40 to 50 mm. US extension advice
for snowy climates goes the other way for the final cut: Illinois says the first and last mowings
"can be slightly shorter" ([Illinois Extension](https://extension.illinois.edu/lawns/mowing-your-lawn)),
and NDSU and Ask Extension recommend a lower final cut against snow mould (summarised in search
results, not read directly). The snow-mould reasoning matters little in lowland southern England: the RHS says snow
mould "develops under prolonged snow cover", while the UK problem, fusarium patch (*Microdochium
nivale*), is driven by surface moisture and lush, high-nitrogen growth, with optimum "12-19°C"
([RHS, fusarium patch](https://www.rhs.org.uk/disease/fusarium-patch-and-snow-mould)). The RHS
does not link fusarium patch to cut height.

**Scale caveat.** RHS heights are well below this automation's 50 mm summer target. RHS's winter figure
(40 mm) is already under 50 mm, so "+5 mm on summer" (55 mm) is the only RHS rule that applies
directly. Navimow's absolute 40 to 50 mm, and no lower than 35 mm, is already met at 50 mm.

## 2. Growth temperature and a growth-potential model

**Thresholds (all daily air temperature unless stated):**

| Source | Threshold | Measure |
| --- | --- | --- |
| Cornell turf | top growth continues "until the average daily temperature is consistently below 50°F" (10 °C); roots grow on "until soil freezes" | daily mean air ([Cornell, know your lawn](https://turf.cals.cornell.edu/lawn/lawn-care-the-easiest-steps-to-an-attractive-environmental-asset/four-steps-to-success/know-your-lawn)) |
| Iowa State | foliage stops when "daytime high temperatures … are consistently below 50 degrees Fahrenheit" | daily max air ([Iowa State FAQ](https://yardandgarden.extension.iastate.edu/faq/when-can-i-stop-mowing-lawn-fall)) |
| PACE Turf (Stowell) | "Cool-season turf grows best 60-75F", "poor growth >80F & <50F"; "Growth potential >50% results in vigorous growth" | mean air ([Haines & Stowell slides](https://www.slideshare.net/slideshow/mlsn-gp-72243194/72243194)) |
| RHS | grows "in temperatures above 7°C" | unspecified ([RHS, November](https://www.rhs.org.uk/advice/in-month/november/lawns)) |
| Husqvarna | "usually not necessary to mow the lawn when it gets colder than approximately 8°C/40°F" (their °F figure is wrong; 8 °C is 46 °F) | unspecified ([Husqvarna UK, KA-70058](https://www.husqvarna.com/uk/support/articles/at-what-temperature-can-i-use-charge-and-store-my-automower-robotic-lawn-mower-ka-70058/)) |
| Navimow (excerpt) | growth "slows significantly" when mean "consistently falls below 10 degrees Celsius"; 6 to 10 °C slowing; below 6 °C "practically no growth"; mow while "above approximately 6–8 °C"; restart "from temperatures above 8–10 °C" | daily mean air ([Navimow, winter break](https://navimow.segway.com/blogs/maintenance/when-do-robotic-lawnmowers-take-their-winter-break)) |
| UK turf practice | Growing Degree Days with base 6 °C, "which reflects the onset of consistent turf growth"; 4 to 6 GDD a day "indicative of good growth" | mean air (Pitchcare, Mark Hunt, summarised from search; [Pitchcare GDD](https://www.pitchcare.com/blogs/news/measuring-growth-how-gdd-supports-smarter-turf-decisions)) |

So the sources cluster: little top growth below a mean of about 6 °C, slow growth from 6 to 10 °C,
normal growth above 10 °C. They agree that **daily mean air temperature** is a workable input.
Soil temperature: no source found gives a UK soil-depth threshold for shoot growth. Soil
temperature does matter for **traffic injury** in frost (section 3).

**Growth potential (GP) model.** Gelernter and Stowell (PACE Turf), first published in *Golf
Course Management* in 2005 ("Improved overseeding programs", the article itself could not be
retrieved):

    GP = exp( -0.5 * ((T - T_opt) / var)^2 )

- T: mean air temperature (daily, or averaged over a week or month).
- Cool-season (C3) grass: T_opt = 20 °C, var = 5.5 in °C
  ([Asian Turfgrass Center](https://www.asianturfgrass.com/post/number-between-1-0-using-the-turfgrass-growth-potential/)).
  PACE's own Fahrenheit form is "68 for C3" and "sd = standard deviation (10 for C3…)"
  ([Haines & Stowell slides](https://www.slideshare.net/slideshow/mlsn-gp-72243194/72243194)).
  These agree: 10 °F is 5.56 °C. The Asian Turfgrass Center warns the variance must match the
  scale; using 10 with °C is a common error ([ATC, calculating GP](https://www.asianturfgrass.com/post/calculating-gp/)).
- Output 0 to 1. Only published interpretation found: GP > 0.5 is "vigorous growth". No source
  gives a "no growth" GP cut-off.
- Reference values (var 5.5): 5 °C 0.02, 6 °C 0.04, 8 °C 0.09, 10 °C 0.19, 12 °C 0.35,
  15 °C 0.66, 20 °C 1.0, 25 °C 0.66, 28 °C 0.35. So the 6/8/10 °C thresholds above sit at
  GP ≈ 0.04/0.09/0.19.
- Limits: assumes one optimum for all cool-season species and ignores light and moisture (ATC
  posts above). It is symmetric, so it also falls in heat.
- UK use: a BIGGA *Greenkeeper International* article (May 2007) discusses the PACE model
  ([MSU archive PDF](https://archive.lib.msu.edu/tic/bigga/gki/article/2007may34.pdf)); it is a
  scanned PDF and could not be read here.

## 3. Frost

- **RHS:** "Never mow wet or frosty grass … Wait until later in the day when the lawn has dried
  out or defrosted" ([RHS, lawn mowing](https://www.rhs.org.uk/lawns/mowing)); "Don't mow or walk
  on frosty grass as this can damage it" ([RHS, how to mow](https://www.rhs.org.uk/lawns/how-to-mow-a-lawn));
  "Avoid walking on a frosty lawn, as this can damage the blades of grass" ([RHS, November](https://www.rhs.org.uk/advice/in-month/november/lawns)).
- **Mechanism:** extension sources attribute frost-traffic injury to ice crystals rupturing leaf
  cells; leaf injury is usually recoverable, crown injury can kill the plant (summarised in search
  results from US extension pages, not read directly).
- **Best evidence (Oregon State, USGA-funded; Kowalewski et al., *USGA Green Section Record*,
  15 March 2024, reprinted in [GCM, May 2024](https://gcmonline.com/research/news/the-effects-of-traffic-on-turf-during-frost-and-freezing-conditions)):**
  - Foot traffic (6 to 48 steps) on frosted annual meadow-grass greens over 8 frost events: no
    injury.
  - One pass of a utility cart on frosted creeping bent: noticeable damage; seven passes, damage
    for over two weeks. Perennial ryegrass showed "unacceptable injury" from morning cart traffic
    at 35 °F (1.7 °C) or below.
  - Cart traffic on frozen soil damaged bent even in the afternoon when the morning had been below
    freezing.
  - "the most-accurate predictor of traffic injury during cold weather was morning soil
    temperature"; injury linked to morning soil temperature below 32 °F (0 °C).
  - Recommendation: mowing, rolling and other maintenance "should still be delayed", and "it
    would not be recommended to use golf carts or maintenance equipment on turf areas during frost
    and frozen soil conditions."
- **Lightweight robot traffic:** no study found on robot mowers specifically. The OSU result puts
  a robot (lighter than a person, but wheeled, turning on the spot and cutting) somewhere between
  "foot traffic, harmless on one species" and "cart, harmful". The cutting itself is maintenance,
  which they say to delay. Manufacturers treat frost as a stop condition:
  - **Husqvarna Frost Guard:** at a scheduled start, if it is "5°C (41°F) or below" the mower
    delays an hour and re-checks hourly; it "will only start when the temperature is higher than
    5°C"; the forecast-based version parks the mower if the forecast goes "below 5°C"
    ([Husqvarna, KA-70060](https://www.husqvarna.com/us/support/articles/protect-your-lawn-with-automower-frost-guard-options-ka-70060/)).
  - **Navimow:** the app has low-temperature notifications and a manual season pause (excerpt,
    Navimow UK last-mow page above). No numeric Navimow frost threshold found.
- **How long to wait after thaw:** no source gives hours. RHS says "later in the day"; OSU says
  judge by morning soil temperature, and do not traffic frozen soil at all that day.

## 4. Waterlogged or very wet ground

- **RHS:** "Never mow if the ground conditions are very soft, wet or frozen"
  ([RHS, lawn mowing](https://www.rhs.org.uk/lawns/mowing)); "Mowing when the soil is very wet can
  cause compaction and produce muddy areas along the wheel ruts"
  ([RHS, how to mow](https://www.rhs.org.uk/lawns/how-to-mow-a-lawn)); autumn lawn work only "as
  long as the soil isn't waterlogged" ([RHS, November](https://www.rhs.org.uk/advice/in-month/november/lawns)).
- **Illinois:** "never advisable to mow when the grass is wet"; mulching mowers do not work well on
  wet grass ([Illinois Extension](https://extension.illinois.edu/lawns/mowing-your-lawn)).
- **Thresholds:** none found for lawns. Agricultural extension work puts peak compaction risk near
  field capacity, "the soil water content after the soil has been saturated and allowed to drain
  freely for about 24 to 48 hours", and says saturated soil is "very prone to rutting" (Iowa State
  and Wisconsin crop extension, summarised from search;
  [Iowa State](https://crops.extension.iastate.edu/encyclopedia/wet-soils-and-potential-compaction)).
  Robot mowers repeat the same lines and turns daily, so ruts are the likely failure mode.

## 5. Spring

- **When:** RHS March: "Mow established lawns when the weather is mild enough and the grass shows
  signs of growth" ([RHS, March lawns](https://www.rhs.org.uk/advice/in-month/march/lawns)).
  Navimow: restart "from temperatures above 8–10 °C" (excerpt, winter-break page above). In lowland
  southern England that is roughly April on average.
- **First-cut height:** RHS: "Ensure the first cut of the season is light, raising the blades
  0.5cm (¼in) higher than the usual cutting height" (RHS, March); "For the first mow in spring or
  when cutting long grass, choose the highest blade setting" ([RHS, lawn mowing](https://www.rhs.org.uk/lawns/mowing)).
  Navimow: first cut leaving "about 4 to 5 cm" (excerpt,
  [Navimow, mowing after winter break](https://navimow.segway.com/blogs/lawn-care/mowing-the-lawn-after-winter-break)).
- **One-third rule:** RHS: "never take off more than one-third of the grass height"
  ([RHS, lawn mowing](https://www.rhs.org.uk/lawns/mowing)). Iowa State: "never remove more than
  one-third of the total leaf area at any one time", e.g. a 3 in lawn is mown at 4.5 in
  ([Iowa State, summer lawn care](https://yardandgarden.extension.iastate.edu/how-to/summer-lawn-care)).
  Physiological basis usually cited: Crider (1955), *Root-growth stoppage resulting from
  defoliation of grass*, USDA Technical Bulletin 1102. The bulletin could not be fetched (HTTP 403
  from [AgEcon Search](https://ageconsearch.umn.edu/record/156759)); secondary summaries report
  that root growth stopped when more than about 40 to 50% of the foliage was removed, for roughly
  6 to 18 days, and did not stop at 40% or less. So "one-third" is a margin under Crider's figure,
  not Crider's own number.
- **Step-down rate:** no source gives mm per day. UC IPM warns against sudden large height changes
  (summarised from search). With daily robot mowing the one-third rule barely binds: at 55 mm a
  5 mm drop plus a day's growth is about 10 to 15% of the leaf.
- **Root timing:** cool-season grasses grow most roots in "April-May and October-November"
  ([Purdue, Reicher 2007](https://turf.purdue.edu/dont-raise-the-mowing-height-during-drought/)),
  which argues against cutting hard in spring.

## 6. Summer heat and drought

- **RHS:** "mow less often and raise the cutting height to let the grass get longer, which should
  encourage deeper rooting"; "If grass growth stops, then take a break from mowing"; let clippings
  "fall back into the grass to act as a mulch and hold in moisture"
  ([RHS, drought care](https://www.rhs.org.uk/lawns/drought-care)). No mm figure.
- **Iowa State:** higher in summer because "The additional leaf area during summer shades and
  cools the crowns"; drought-dormant brown lawns should not be mown: "Pedestrian and mower traffic
  could damage the turf" ([Iowa State, summer lawn care](https://yardandgarden.extension.iastate.edu/how-to/summer-lawn-care)).
- **How much:** US extension figures are +½ in (13 mm) to +1 in (25 mm) (Gwinnett County
  Extension and University of Minnesota, summarised from search). The automation's 50 to 70 mm (+20 mm) sits
  inside that range.
- **Disagreement, Purdue (Reicher, 2007):** raising height *during* drought on unirrigated turf is
  "a very bad decision" because the plant must "support more leaf material with the same amount
  of roots"; better to mow "as high as can be tolerated … and stick with that height
  season-long" ([Purdue](https://turf.purdue.edu/dont-raise-the-mowing-height-during-drought/)).
  For a robot, raising the deck does not lengthen grass; it mainly stops cutting until the grass
  grows into the new height, which is close to RHS's "take a break from mowing".
- **Temperature thresholds:** PACE: "poor growth >80F" (27 °C) for cool-season turf (slides
  above). GP from a daily mean of 25 °C is 0.66, of 28 °C 0.35. No rainfall threshold found.

## 7. Robot-mower manufacturer guidance

- **Navimow (excerpts; navimow.com pages returned HTTP 429 when fetched):** winter break when the
  daily mean "consistently falls below 10 degrees Celsius" or frost threatens; mow while "above
  approximately 6–8 °C"; last cut 4 to 5 cm, not below about 3.5 cm; restart above 8 to 10 °C with
  a first cut leaving 4 to 5 cm. Store "dry and frost-proof" at 5 to 45 °C; app has Help and
  Feedback > Winter Storage > Begin Hibernating
  ([Navimow, store before winter](https://navimow.com/blogs/navimow-academy/how-to-store-navimow-before-winter)).
  Another Navimow blog suggests a final cut of "2 to 2.5 inches" (51 to 64 mm) for US cool-season
  lawns ([Navimow, when to stop mowing before winter](https://navimow.com/blogs/lawn-care/when-to-stop-mowing-your-lawn-before-winter)),
  so Navimow's own blogs disagree by region. Segway says the X4 has a physical rain sensor plus
  online weather, and an app setting for maximum mowing temperature
  ([Segway NZ blog](https://www.segway.co.nz/blogs/blog/how-navimow-decides-whether-or-not-to-mow-in-sunny-rainy-and-frosty-conditions), excerpt).
  The X-series operating temperature range was not found; the manual is the place to check.
- **Husqvarna:** operation "0–50" °C, charging "0–45" °C; mowing usually unnecessary below about
  8 °C; Frost Guard at 5 °C as above ([KA-70058](https://www.husqvarna.com/uk/support/articles/at-what-temperature-can-i-use-charge-and-store-my-automower-robotic-lawn-mower-ka-70058/), [KA-70060](https://www.husqvarna.com/us/support/articles/protect-your-lawn-with-automower-frost-guard-options-ka-70060/)).
- **Third party, weak:** Sunseeker's blog says never mow within 48 hours of forecast frost
  (summarised from search). No agronomic basis given; not used below.

These are primary for what the machines do, not for agronomy.

## 8. Mulching and little-and-often

- Clippings from frequent mowing are small, "break down readily", do not cause thatch, and return
  nutrients ([Illinois Extension](https://extension.illinois.edu/lawns/mowing-your-lawn)); RHS
  says leave them in dry weather to hold moisture ([RHS, drought care](https://www.rhs.org.uk/lawns/drought-care)).
- Trials of autonomous versus rotary mowing on tall fescue (University of Pisa): higher turf
  quality, denser and finer-leaved turf with the robot (7.3 vs 6.4 quality; Grossi et al. 2016,
  *HortTechnology* 26(6), [ASHS](https://journals.ashs.org/view/journals/horttech/26/6/article-p825.xml));
  but also more weed cover, which the authors attribute to the constant cutting height letting
  creeping weeds spread sideways (Pirchio et al. 2018, *Agronomy* 8(2):15,
  [DOAJ record](https://doaj.org/article/52899e5f4fc04b1b8cf5feeefccf2a8d), abstract via search).
- What changes for a robot mower: the one-third rule almost never binds in steady state, because daily
  growth is a few mm. The risks shift to (a) lowering the deck faster than the grass can adapt,
  (b) traffic: a robot crosses the lawn every day, so frost, frozen soil, waterlogging and
  dormant-drought rules matter more than for a weekly mower, and (c) mowing into cold evenings,
  if the schedule runs into the evening.

---

## Rules this suggests for the automation

Inputs: daily mean air temperature `T` ((max + min) / 2, local sensor or forecast), 7-day mean
`T7`, `GP7 = exp(-0.5 * ((T7 - 20) / 5.5)^2)`, current air temperature, overnight minimum, and
rain in the last 24 h. Summer `target` stays 50 mm; `winter_height` = target + 5 mm = 55 mm.

1. **Season regime from T7** (section 2):
   - `T7 ≥ 10 °C` (GP7 ≥ 0.19): growing. Normal rules.
   - `6 ≤ T7 < 10 °C`: slow. Height ≥ `winter_height`, never lower; mow only on days that pass
     rules 4 and 5.
   - `T7 < 6 °C` (GP7 < 0.04): dormant. Do not mow; hold height. Optional Navimow "hibernate"
     only if this lasts several weeks.
2. **Autumn raise** (sections 1, 5): from 1 September, when `T7 < 12 °C` (GP ≈ 0.35, early to
   mid-October in lowland southern England), raise to `winter_height` at once. Raise while the grass is still growing
   so it fills the new height before November. Never set below 40 mm from October to March
   (Navimow ≥ 35 mm, RHS ~40 mm).
3. **Raising is unrestricted; lowering is rate-limited** (sections 5, 8): lower by at most 5 mm
   per 2 days (one full coverage cycle), and only when `T7 ≥ 10 °C` and no heat or drought flag
   is set.
4. **Frost and cold** (section 3): do not start, and send the mower home, when current air temperature
   ≤ 5 °C (Husqvarna's threshold). Skip the whole day if the overnight minimum was ≤ 0 °C and it
   has not risen above 5 °C, or if the ground is known to be frozen (OSU: frozen soil means no
   traffic at all that day). From October to April, end the daily window when the air
   temperature falls below 5 °C instead of running late into the evening.
5. **Wet ground** (section 4): rely on the X4 rain sensor for rain; also skip the day after
   ≥ 10 mm in 24 h from November to March, when drying is slow. The 10 mm figure is a heuristic,
   not sourced: tune it by looking for ruts.
6. **Spring restart and step-down** (section 5): resume mowing when `T7 ≥ 8 °C` for 5 days. First
   cuts at `max(winter_height, measured_or_estimated_length × 2/3)` rounded up to 5 mm (one-third
   rule). Then step down 5 mm per 2 days (rule 3) to `target`, and only once `T7 ≥ 10 °C`.
7. **Heat and drought** (section 6): keep the existing 70 mm protective height but treat it as
   "stop cutting", not "grow longer". Suggested triggers: daily max ≥ 27 °C, or daily mean
   ≥ 25 °C (GP < 0.66), or a dry-spell flag. If the lawn is brown and dormant, pause mowing
   entirely (Iowa State). Return to `target` via rule 3 once rain has returned and growth
   resumes.

### Open questions

- The mower's manual (Navimow X-series): operating and charging temperature range, and whether it has a built-in
  frost or low-temperature stop that the automation should defer to.
- Winter height 55 mm or simply hold 50 mm: RHS says +5 mm, Navimow's absolute range is already
  met at 50 mm, and no source ties winter height to fusarium patch risk either way.
- Frost wait after thaw: no source gives hours. Is a local soil temperature sensor (OSU's
  predictor) worth adding?
- Wet-ground threshold: none published for lawns. A soil moisture sensor would replace the
  rainfall heuristic.
- GP thresholds are not validated for UK lawns; the 6/8/10 °C cut-offs come from practitioner and
  manufacturer advice, not trials.
- Modelled or regional weather can miss a local frost hollow. A local temperature sensor would
  settle it.
- Drought: Purdue argues against raising height mid-drought on unirrigated turf, RHS and others
  for it. For a robot the practical difference may be small, since raising mostly means not
  cutting.
- Crider (1955) primary text not read; the 40 to 50% figure is from secondary summaries.
