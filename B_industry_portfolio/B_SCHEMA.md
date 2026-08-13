# SCHEMA — 조사자 B 데이터 정의서

데이터를 읽거나 쓰기 전에 이 문서를 확인한다. 통제어휘 밖의 값을 넣으면 집계가 깨진다.

---

## 통제어휘 (전 파일 공통)

### status — 사업의 진행 단계
| 값 | 정의 | 판정 기준 |
|---|---|---|
| `계획` | 발표·구상 단계 | 보도자료·계획문서에 언급만 있고 예산 미확인 |
| `결정` | 예산편성 또는 선정 완료 | 본예산 편성, 공모 선정, 심의 가결 |
| `모집` | 공고 진행 중 | 신청 접수 기간이 열려 있음 |
| `운영` | 집행 중 | 사업이 실제로 돌아가는 중 |
| `종료` | 완료 | 사업기간 종료 또는 최종보고서 발간 |

### evidence_status — 정책 정보의 출처 등급 (B1)
| 값 | 정의 |
|---|---|
| `PRIMARY_VERIFIED` | 공고문·예산서·의회자료 등 1차 출처 확인 |
| `SECONDARY_PRESS_ONLY` | 언론보도만 확인, 원문 미확인 |
| `CONFLICTING_FIGURES` | 공개 출처 간 수치 불일치 |
| `UNVERIFIED` | 존재만 확인, 내용 미확인 |

> 승격은 실제 원문 확인 시에만. `CHANGELOG.md`에 확인한 문서명을 남긴다.

### evidence_grade — 수요신호의 근거 등급 (B2)
| 값 | 정의 | 예 |
|---|---|---|
| `A` | 국가승인통계·공식기록 | 산업기술인력 수급실태조사, 의회 회의록 |
| `B` | 공공기관 연구보고서 | 한국은행 인천본부, 인천연구원, KISTI |
| `C` | 언론보도 | 지역일간지, 전문지 |
| `D` | 사업주체 자기서술 | 사업단 홈페이지의 사업 정당화 문구 |

> `D`는 수요 근거로 단독 사용 금지. 반드시 상위 등급으로 교차검증한다.

### sustained_or_spike — 수요의 시간성 (B2)
| 값 | 정의 | 판정 방법 |
|---|---|---|
| `SUSTAINED` | 3~5년 이상 지속 | 서로 다른 연도의 서로 다른 기관 문서에 반복 등장 |
| `SPIKE` | 최근 1~2년 | 단일 시점 문서에만 등장하며 사업 실적성 |
| `FORECAST` | 전망치 | 미래 시점 예측값. **현재 수요와 섞지 말 것** |
| `POLICY_TREND` | 정책유행 의심 | 기업 수요 출발 근거 없이 정책 문서에만 등장 |

### consideration_status — 기존사업 고려 여부 (B3)
| 값 | 정의 |
|---|---|
| `EXPLICIT` | 사업 문서가 기존사업을 명시적으로 검토하거나 역할을 나눔 |
| `REFERENCED` | 언급은 있으나 역할분담 근거는 없음 |
| `INFERRED` | 정황상 추론 가능 (근거를 note에 명시) |
| `NOT_PUBLICLY_VERIFIABLE` | 공개자료로 확인 불가 |

### priority — 결측 데이터 확보 우선순위 (B5)
| 값 | 정의 |
|---|---|
| `P1` | 없으면 후속 분석이 불가능하거나 결론이 뒤집힘 |
| `P2` | 판정 정밀도를 올리는 데 필요 |
| `P3` | 있으면 좋음 |

### strategic_industry
`바이오` `반도체` `로봇` `디지털데이터` `미래차` `항공` `공통`
복합값은 `+`로 연결한다 (예: `바이오+디지털데이터`).
**배타적 분류가 아니다.** 합계 시 중복 계상 규칙을 먼저 정할 것.

---

## B1_policy_portfolio.csv (52행 × 24열)

| 컬럼 | 설명 | 비고 |
|---|---|---|
| `stable_policy_id` | 고유 ID | 재사용 금지 |
| `version` | 이 행의 갱신일 | YYYY-MM-DD |
| `strategic_industry` | 전략산업 태그 | 통제어휘 |
| `policy_name` | 사업명 | 공식 명칭 우선 |
| `status` | 진행 단계 | 통제어휘 |
| `owner_department` | 소관 부처·부서 | |
| `executor` | 실제 수행기관 | 소관과 다를 수 있음 |
| `target` | 지원 대상 | 누구에게 |
| `problem` | 사업이 표방하는 문제 | 무엇을 해결한다고 주장하는가 |
| `intervention` | 개입 수단 | 무엇을 어떻게 |
| `industry` | KSIC 기준 산업 | 정책 라벨과 다를 수 있음 |
| `occupation` | 대상 직무 | |
| `skill` | 대상 역량 | |
| `geography` | 공간 범위 | **2026-07-01 개편 기준, 구명칭 병기** |
| `application_period` | 신청 기간 | |
| `delivery_period` | 사업 수행 기간 | |
| `budget` | 예산 | 불일치 시 `CONFLICTING:` 접두 후 전부 병기 |
| `budget_source` | 재원 | 국비/시비/구비/민간 |
| `kpi` | 약속한 성과지표 | |
| `reported_result` | 발표된 성과 | |
| `upstream_policy` | 선행·상위 사업 | ID 또는 명칭 |
| `downstream_policy` | 후속·하위 사업 | ID 또는 명칭 |
| `source_url` | 출처 | 복수는 ` \| `로 구분 |
| `evidence_status` | 출처 등급 | 통제어휘 |

## B2_demand_signal.csv (29행 × 14열)

| 컬럼 | 설명 |
|---|---|
| `signal_id` | 고유 ID |
| `strategic_industry` | 전략산업 태그 |
| `problem_type` | 병목 유형 (인력/기술/판로/금융/시설/공급망/구조 등) |
| `industry` | 대상 산업 |
| `occupation_or_function` | 직무 또는 기능 |
| `geography` | 관측 공간 단위 |
| `period` | 관측 시점 |
| `value` | 측정값 |
| `unit` | 단위 |
| `population_definition` | **모집단 정의. 이게 없으면 값이 무의미하다** |
| `source_url` | 출처 |
| `evidence_grade` | 근거 등급 |
| `proxy_limit` | **이 지표의 한계. 반드시 채운다** |
| `sustained_or_spike` | 시간성 |

> `proxy_limit`가 비어 있는 행은 미완성으로 간주한다.

## B3_linkage_evidence.csv (22행 × 13열)

| 컬럼 | 설명 |
|---|---|
| `policy_a` / `policy_b` | 비교 대상 사업 ID |
| `cross_industry` | 산업 교차 여부 (YES/NO) |
| `shared_target` | 대상 중복 (YES/PARTIAL/NO) |
| `shared_function` | 기능 중복 |
| `explicit_reference` | 상호 명시 참조 여부 |
| `handoff` | 인계·추천 관계 |
| `shared_company_pool` | 공통 기업풀 |
| `shared_kpi` | 공통 성과지표 |
| `timing_relation` | 시간 관계 |
| `consideration_status` | 기존사업 고려 여부 |
| `evidence_id` | 근거 ID (E-xx) |
| `note` | **판정 근거 + 반대가설. 가장 중요한 컬럼** |

> `note`의 반대가설을 배제하지 않은 채 "중복"으로 인용하는 것은 금지.

## B5_missing_data_requests.csv (17행 × 10열)

| 컬럼 | 설명 |
|---|---|
| `request_id` | 고유 ID |
| `strategic_industry` | 관련 산업 |
| `needed_field` | 필요한 데이터 |
| `why_needed` | 어느 판정에 쓰이는지 |
| `likely_owner` | 보유 가능 기관 |
| `public_or_internal` | 공개/내부 |
| `legal_or_contract_issue` | 법적·계약적 제약 |
| `minimum_aggregate` | 원자료가 안 되면 이 집계 수준까지는 요청 |
| `fallback_proxy` | 끝내 못 구할 때의 대체 지표 |
| `priority` | P1/P2/P3 |

---

## 새 행을 추가할 때

1. `source_url`이 있는가? 없으면 추가하지 않는다.
2. 통제어휘를 벗어난 값이 있는가? 없어야 한다.
3. B2라면 `population_definition`과 `proxy_limit`를 채웠는가?
4. B3라면 `note`에 반대가설을 적었는가?
5. 확인 못 한 필드는 `UNKNOWN`으로 둔다. 추정치를 넣지 않는다.
6. `scripts/`의 파이썬을 수정하고 재실행한다. CSV 직접 편집 금지.
7. `CHANGELOG.md`에 기록한다.
