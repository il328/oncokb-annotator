## Cell: Fit (labels -> model + threshold)

### What comes out
| object | what it is | used by |
|---|---|---|
| `final_model` | HGB trained on all 3,575 labeled variants | scoring cell |
| `THRESHOLD` = 0.1397 | the cutoff turning probability into a call | scoring cell |
| `proba_cv` | 3,575 honest predictions, one per training variant | QA cell, recall-90 cell, coverage cell |

### The cell does two separate jobs

**BUILD** — one line: `final_model = hgb.fit(X, y)`
Trains on all 3,575 rows. This is the model that gets deployed.

**MEASURE** — five lines. Builds 5 *throwaway* models, each trained on 80%,
each predicting the 20% it did not see. They are discarded immediately.
They exist only to answer:
  1. is this kind of model any good?  -> AUROC 0.898
  2. where should the cutoff go?      -> THRESHOLD 0.1397

The two jobs share `X`, `y`, and `hgb`. Only difference is how much data each fit sees
(80% for the throwaways, 100% for final_model).

Order matters one way: the measuring must run while `hgb` is still unfitted.

### Key objects
- `X` = `lab[MODEL_TOOLS].values` -> (3575, 8) array. Names stripped, so the model
  identifies features BY POSITION. `MODEL_TOOLS` is the only thing pinning the order.
- `y` = `lab["label"].values` -> 3,575 zeros and ones.
      1 = OncoKB Oncogenic / Likely Oncogenic (824)
      0 = OncoKB Likely Neutral, or ClinVar benign (2,751)
- `cv` = the *plan* for splitting into 5 stratified, shuffled groups. Holds no data.
- `proba_cv` = (3575,) array of floats 0-1. P(oncogenic) per variant, each from a
  model that never trained on that variant. Aligned position-by-position with `y`.

### How THRESHOLD is calculated

Sort the training variants by model score, highest first. Slide a line rightward one
variant at a time. Everything left of the line is called oncogenic.

score  0.90  0.66  0.61  0.44  0.35  0.28  0.22  0.15  0.10  0.05
truth  BAD   fine  BAD   BAD   fine  BAD   fine  fine  fine  fine
       (BAD = label 1, 4 of them.  fine = label 0, 6 of them.)

 line after   caught   false alarms   caught - false alarms
     1         1/4         0/6              0.25
     3         2/4         1/6              0.33
     4         3/4         1/6              0.58
     6         4/4         2/6              0.67   <- best
     7         4/4         3/6              0.50
    10         4/4         6/6              0.00

Position 6 wins: every BAD found, only 2 false alarms. Moving further right catches
nothing new (already at 4/4) and only adds false alarms. The score sitting at
position 6 becomes THRESHOLD.

Code names for the same three columns:
  `thr` = the score at each line position
  `tpr` = caught fraction        (recall)
  `fpr` = false-alarm fraction
  `tpr - fpr` = Youden's J, the rightmost column
  `.argmax()` returns the ROW NUMBER of the best J, not the value
  `thr[that row]` = THRESHOLD

`roc_curve` does not take a cutoff as input. It tries every distinct score as a cutoff
and returns one row per attempt.

### The assumption inside `tpr - fpr`
Subtracting weights one missed oncogenic variant and one false alarm EQUALLY.



### Truth only exists on the training side
3,575 training variants have both a score and a known answer -> the line can be drawn.
13,926 Fisher missense variants have a score and NO answer -> the line gets applied.

### Decisions log
| line | decision | alternative not taken |
|---|---|---|
| `StratifiedKFold(shuffle=True)` | shuffles rows before splitting | `GroupKFold` on gene. `lab` is coordinate-sorted, so shuffling puts same-gene variants in both train and test folds. 0.898 is a WITHIN-GENE estimate. |
| `HistGradientBoostingClassifier()` | all defaults | no class weighting despite 23/77 imbalance; no hyperparameter search. Note the RF in the next cell DID get `class_weight="balanced"` — the two are not compared on equal footing. |
| `cross_val_predict` | returns predictions | `cross_val_score` returns 5 AUROCs and nothing reusable. Cost of this choice: one pooled AUROC with no ± spread. |
| `(tpr - fpr).argmax()` | Youden | equal cost weighting; see above |
| `hgb.fit(X, y)` at the end | refit on 100% | could have kept the 5 fold models via `cross_validate(return_estimator=True)` and averaged them |
