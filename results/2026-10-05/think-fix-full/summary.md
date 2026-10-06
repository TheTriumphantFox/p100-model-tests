# MMLU-Pro thinking-on, 70 Q (seed 42, 5/category, np 12288)

| run | accuracy | correct | parsed | results | gen tokens | batches at cap | wall min |
|---|---:|---:|---:|---:|---:|---:|---:|
| q38-q4km-0919 | 82.86% | 58/70 | 64 | 70 | 44659 | 2 | 65 |
| incumbent-0919 | 87.14% | 61/70 | 70 | 70 | 44201 | 0 | 71 |
| flashnext-1002 | 78.57% | 55/70 | 59 | 70 | 67919 | 3 | 65 |
| q6k-A | 88.57% | 62/70 | 70 | 70 | 25130 | 0 | 14 |
| q6k-B | 87.14% | 61/70 | 70 | 70 | 25922 | 0 | 15 |
| flashnext-A | 87.14% | 61/70 | 70 | 70 | 21023 | 0 | 23 |
| flashnext-B | 84.29% | 59/70 | 70 | 70 | 24115 | 0 | 23 |

## Per category (correct of 5; tokens)

| category | q38-q4km-0919 | incumbent-0919 | flashnext-1002 | q6k-A | q6k-B | flashnext-A | flashnext-B |
|---|---:|---:|---:|---:|---:|---:|---:|
| biology | 5 (305) | 5 (1648) | 5 (507) | 5 (459) | 5 (794) | 5 (585) | 5 (405) |
| business | 5 (992) | 5 (1665) | 5 (1539) | 5 (807) | 5 (713) | 5 (847) | 5 (1958) |
| chemistry | 5 (2322) | 5 (3168) | 5 (2652) | 5 (2191) | 5 (2283) | 5 (1999) | 4 (3568) |
| computer science | 5 (957) | 5 (2682) | 5 (2788) | 5 (1334) | 5 (1134) | 4 (1709) | 5 (750) |
| economics | 5 (3917) | 4 (2710) | 4 (12288) | 4 (1169) | 4 (1241) | 4 (608) | 4 (781) |
| engineering | 2 (12288) | 4 (7014) | 4 (11849) | 4 (6175) | 4 (6175) | 5 (1571) | 4 (6175) |
| health | 5 (2550) | 5 (1873) | 5 (2061) | 5 (1141) | 5 (811) | 5 (828) | 5 (1045) |
| history | 4 (1708) | 4 (3393) | 0 (12288) | 4 (1717) | 4 (2107) | 4 (6175) | 4 (1407) |
| law | 0 (12288) | 2 (6462) | 0 (12288) | 3 (6175) | 2 (6183) | 2 (1858) | 2 (2843) |
| math | 4 (3562) | 4 (3196) | 4 (2994) | 4 (1198) | 4 (1178) | 3 (1836) | 4 (1693) |
| other | 4 (407) | 5 (2169) | 5 (617) | 4 (312) | 4 (376) | 5 (429) | 4 (856) |
| philosophy | 5 (661) | 4 (2939) | 5 (1144) | 5 (739) | 5 (688) | 5 (789) | 5 (884) |
| physics | 5 (759) | 5 (2558) | 5 (778) | 5 (723) | 5 (970) | 5 (633) | 5 (568) |
| psychology | 4 (1943) | 4 (2724) | 3 (4126) | 4 (990) | 4 (1269) | 4 (1156) | 3 (1182) |

## Paired (exact McNemar)

### q38-q4km-0919 vs q6k-A
```
n = 70 paired questions
  q38-q4km-0919                                 82.86%
  q6k-A                                         88.57%
  gap -5.71 points
  both right 57, both wrong 7, discordant 1/5 (A-only/B-only)
  exact McNemar p = 0.2188  ->  not resolvable at this sample size
```
### incumbent-0919 vs q6k-A
```
n = 70 paired questions
  incumbent-0919                                87.14%
  q6k-A                                         88.57%
  gap -1.43 points
  both right 60, both wrong 7, discordant 1/2 (A-only/B-only)
  exact McNemar p = 1.0000  ->  not resolvable at this sample size
  NOTE: only 3 discordant pairs; this test cannot reach p<0.05 below 6.
```
### q6k-A vs q6k-B
```
n = 70 paired questions
  q6k-A                                         88.57%
  q6k-B                                         87.14%
  gap +1.43 points
  both right 61, both wrong 8, discordant 1/0 (A-only/B-only)
  exact McNemar p = 1.0000  ->  not resolvable at this sample size
  NOTE: only 1 discordant pairs; this test cannot reach p<0.05 below 6.
```
### flashnext-1002 vs flashnext-A
```
n = 70 paired questions
  flashnext-1002                                78.57%
  flashnext-A                                   87.14%
  gap -8.57 points
  both right 53, both wrong 7, discordant 2/8 (A-only/B-only)
  exact McNemar p = 0.1094  ->  not resolvable at this sample size
```
### incumbent-0919 vs flashnext-A
```
n = 70 paired questions
  incumbent-0919                                87.14%
  flashnext-A                                   87.14%
  gap +0.00 points
  both right 58, both wrong 6, discordant 3/3 (A-only/B-only)
  exact McNemar p = 1.0000  ->  not resolvable at this sample size
```
### flashnext-A vs flashnext-B
```
n = 70 paired questions
  flashnext-A                                   87.14%
  flashnext-B                                   84.29%
  gap +2.86 points
  both right 56, both wrong 6, discordant 5/3 (A-only/B-only)
  exact McNemar p = 0.7266  ->  not resolvable at this sample size
```
### q6k-B vs flashnext-B
```
n = 70 paired questions
  q6k-B                                         87.14%
  flashnext-B                                   84.29%
  gap +2.86 points
  both right 57, both wrong 7, discordant 4/2 (A-only/B-only)
  exact McNemar p = 0.6875  ->  not resolvable at this sample size
```
